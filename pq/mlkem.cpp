#include <openssl/base.h>
#include <openssl/bytestring.h>
#include <openssl/mem.h>
#include <openssl/mlkem.h>

#include <fstream>
#include <memory>
#include <vector>
#include <cstring>
#include <iostream>

const char b64chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
int b64invs[] = {62, -1, -1, -1, 63, 52, 53, 54, 55, 56, 57, 58,
                 59, 60, 61, -1, -1, -1, -1, -1, -1, -1, 0, 1, 2, 3, 4, 5,
                 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                 21, 22, 23, 24, 25, -1, -1, -1, -1, -1, -1, 26, 27, 28,
                 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                 43, 44, 45, 46, 47, 48, 49, 50, 51};

// Base64 validation function
bool b64_isvalidchar(char c)
{
    return (isalnum(c) || c == '+' || c == '/' || c == '=');
}

size_t b64_encoded_size(size_t inlen)
{
    size_t ret = inlen;
    if (inlen % 3 != 0)
        ret += 3 - (inlen % 3);
    return (ret / 3) * 4;
}

char *b64_encode(const unsigned char *in, size_t len)
{
    if (in == nullptr || len == 0)
        return nullptr;

    size_t elen = b64_encoded_size(len);
    auto out = std::make_unique<char[]>(elen + 1);
    out[elen] = '\0';

    for (size_t i = 0, j = 0; i < len; i += 3, j += 4)
    {
        size_t v = in[i];
        v = i + 1 < len ? v << 8 | in[i + 1] : v << 8;
        v = i + 2 < len ? v << 8 | in[i + 2] : v << 8;

        out[j] = b64chars[(v >> 18) & 0x3F];
        out[j + 1] = b64chars[(v >> 12) & 0x3F];
        out[j + 2] = (i + 1 < len) ? b64chars[(v >> 6) & 0x3F] : '=';
        out[j + 3] = (i + 2 < len) ? b64chars[v & 0x3F] : '=';
    }

    return out.release();  // Transfer ownership to caller
}

size_t b64_decoded_size(const char *in)
{
    if (!in)
        return 0;
    
    size_t len = strlen(in);
    size_t ret = (len / 4) * 3;
    
    for (size_t i = len; i-- > 0;)
        if (in[i] == '=') ret--;
        else break;

    return ret;
}

bool b64_decode(const char *in, unsigned char *out, size_t outlen)
{
    if (!in || !out)
        return false;

    size_t len = strlen(in);
    if (outlen < b64_decoded_size(in) || len % 4 != 0)
        return false;

    for (size_t i = 0, j = 0; i < len; i += 4, j += 3)
    {
        if (!b64_isvalidchar(in[i])) return false;

        int v = b64invs[in[i] - 43];
        v = (v << 6) | b64invs[in[i + 1] - 43];
        v = (in[i + 2] == '=') ? v << 6 : (v << 6) | b64invs[in[i + 2] - 43];
        v = (in[i + 3] == '=') ? v << 6 : (v << 6) | b64invs[in[i + 3] - 43];

        out[j] = (v >> 16) & 0xFF;
        if (in[i + 2] != '=') out[j + 1] = (v >> 8) & 0xFF;
        if (in[i + 3] != '=') out[j + 2] = v & 0xFF;
    }

    return true;
}

// C function interface
extern "C" {
    uint8_t** gen_key_and_ciphertext(char *key_file_name);
    char* get_key_from_ciphertext(char *ct, char *key_file_name);
    int generate_keys(char* pub_filename, char* priv_filename);
}

char *get_key_from_ciphertext(char *ct, char *key_file_name)
{
    std::ifstream priv_key_file(key_file_name, std::ios::binary | std::ios::ate);
    if (!priv_key_file)
        return nullptr;

    std::streamsize size = priv_key_file.tellg();
    priv_key_file.seekg(0, std::ios::beg);

    std::vector<uint8_t> private_key_data(size);
    if (!priv_key_file.read(reinterpret_cast<char*>(private_key_data.data()), size))
        return nullptr;

    MLKEM768_private_key priv_key;
    if (!MLKEM768_private_key_from_seed(&priv_key, private_key_data.data(), size))
        return nullptr;

    uint8_t shared_secret[MLKEM_SHARED_SECRET_BYTES];
    auto ct_decoded = std::make_unique<uint8_t[]>(MLKEM768_CIPHERTEXT_BYTES);
    if (!b64_decode(ct, ct_decoded.get(), MLKEM768_CIPHERTEXT_BYTES))
        return nullptr;

    if (!MLKEM768_decap(shared_secret, ct_decoded.get(), MLKEM768_CIPHERTEXT_BYTES, &priv_key))
        return nullptr;

    return b64_encode(shared_secret, MLKEM_SHARED_SECRET_BYTES);
}

uint8_t **gen_key_and_ciphertext(char *key_file_name)
{
    std::ifstream pub_key_file(key_file_name, std::ios::binary | std::ios::ate);
    if (!pub_key_file)
        return nullptr;

    std::streamsize size = pub_key_file.tellg();
    pub_key_file.seekg(0, std::ios::beg);

    std::vector<uint8_t> public_key_data(size);
    if (!pub_key_file.read(reinterpret_cast<char*>(public_key_data.data()), size))
        return nullptr;

    MLKEM768_public_key pub_key;
    CBS public_key_cbs;
    CBS_init(&public_key_cbs, public_key_data.data(), public_key_data.size());

    if (!MLKEM768_parse_public_key(&pub_key, &public_key_cbs))
        return nullptr;

    uint8_t ciphertext[MLKEM768_CIPHERTEXT_BYTES];
    uint8_t shared_secret[MLKEM_SHARED_SECRET_BYTES];
    
    MLKEM768_encap(ciphertext, shared_secret, &pub_key);

    auto key_and_ciphertext = std::make_unique<uint8_t*[]>(2);
    key_and_ciphertext[0] = reinterpret_cast<uint8_t*>(b64_encode(shared_secret, MLKEM_SHARED_SECRET_BYTES));
    key_and_ciphertext[1] = reinterpret_cast<uint8_t*>(b64_encode(ciphertext, MLKEM768_CIPHERTEXT_BYTES));

    return key_and_ciphertext.release();
}

int generate_keys(char* pub_filename, char* priv_filename)
{
    auto private_key = std::make_unique<MLKEM768_private_key>();
    auto public_key = std::make_unique<MLKEM768_public_key>();
    uint8_t priv_seed[MLKEM_SEED_BYTES];
    uint8_t encoded_public_key[MLKEM768_PUBLIC_KEY_BYTES];

    MLKEM768_generate_key(encoded_public_key, priv_seed, private_key.get());
    MLKEM768_public_from_private(public_key.get(), private_key.get());

    CBB out_pub;
    if (!CBB_init(&out_pub, MLKEM768_PUBLIC_KEY_BYTES) ||
        !MLKEM768_marshal_public_key(&out_pub, public_key.get()))
        return -1;

    uint8_t *out_pub_data;
    size_t out_pub_len;
    if (!CBB_finish(&out_pub, &out_pub_data, &out_pub_len))
        return -1;

    std::ofstream pub_key_file(pub_filename, std::ios::binary);
    if (!pub_key_file)
        return -1;
    pub_key_file.write(reinterpret_cast<const char*>(out_pub_data), out_pub_len);

    std::ofstream priv_key_file(priv_filename, std::ios::binary);
    if (!priv_key_file)
        return -1;
    priv_key_file.write(reinterpret_cast<const char*>(priv_seed), MLKEM_SEED_BYTES);

    OPENSSL_free(out_pub_data);

    return 0;
}
