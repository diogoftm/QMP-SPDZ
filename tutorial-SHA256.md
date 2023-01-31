"""
This implementation is used for the following paper:

    https://private-database-query.nature.com


Done so far:

1. Compute SHA256 with the initial registers and empty message (working)

```
sha256 = Circuit('sha256')

sb512 = sbits.get_type(512)
siv256 = sbitintvec.get_type(256)
siv512 = sbitintvec.get_type(512)

state = siv256(0x6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19)
secret = siv512(sb512(0x1 << 511))

result = sha256(secret, state)

result.elements()[0].reveal().print_reg()
print_ln("SHA256 is %s", result.elements()[0].reveal())
```

2. Decompose and truncate `sbitint` type into `bits` (working)

By hand looks like this:

```
si8 = sbitint.get_type(8)

te100110 = si8(38)

bits = te100110.bit_decompose()
res = te100110.get_type(3).bit_compose(bits[:3])
```

Using `TruncPr` function:

```
trunc_res = te100110.TruncPr(3,0)
trunc_res_3 = te100110.TruncPr(6,4)
```

Note :: TruncPr returns a sbitint type elements as well. Also, for TruncPr(k, m), k > m, 
kth index is excluded and mth index is included.


3. Reveal sbitint to a particular player

sbitint does not have implemented the `reveal_to()` method. Therefore, we
have to convert it into `sint` type.

```
sint_trunc_res_110 = sint.bit_compose(sint(trunc_res))
print_ln_to(0, "Now, in the sint version: %s", sint_trunc_res_110.reveal_to(0))
```

4. Print the result to file:

```
./mascot-party.x -N 2 -I -p 0 private_database_query > output_0.txt
```

5. Looping through the elements is working


To be done:

1. Hardcode some message in order to get right results. [x]

10110101 10110101 10110101 10110101 
10110101 10110101 10110101 10110101
10110101 10110101 10110101 10110101
10000000 00000000 00000000 00000000
00000000 00000000 00000000 00000000
00000000 00000000 00000000 00000000
00000000 00000000 00000000 00000000
00000000 00000000 00000000 00000000
00000000 00000000 00000000 00000000
00000000 00000000 00000000 00000000
00000000 00000000 00000000 00000000
00000000 00000000 00000000 00000000
00000000 00000000 00000000 00000000
00000000 00000000 00000000 00000000
00000000 00000000 00000000 00000000
00000000 00000000 00000000 01100000

2. Hardcode some message with loop. [ ]
3. Input from parties and understand types to get the hash message working properly. [ ] <--- doing

## This does not work because it generates several runs instead of joining

msg_buffer_1 = sb256(0b1011010110110101101101011011010110110101101101011011010110110101101101011011010110110101101101011000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
msg_buffer_2 = sb256(0b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001100000)
chain_val = sha256(siv512([msg_buffer_2, msg_buffer_1]), sbitvec([chaining]))


## This works: use bit_decompose.
# Note::v_bits is a vector in big/little-endian.

sb8 = sbits.get_type(4)
val = sb8(0b0110)
p = sb8(0b0110)
v_bits = val.bit_decompose()[:4]
p_bits = p.bit_decompose()[:4]
test = bit_compose(v_bits + p_bits)


print_ln("Testing. It should be: 01100110 = %s", test.reveal())
print_ln("Testing. It should be: 0 = %s", v_bits[0].reveal())
print_ln("Testing. It should be: 1 = %s", v_bits[1].reveal())
print_ln("Testing. It should be: 1 = %s", v_bits[2].reveal())
print_ln("Testing. It should be: 0 = %s", v_bits[3].reveal())
print_ln("Testing. It should be: 0 = %s", p_bits[0].reveal())
print_ln("Testing. It should be: 1 = %s", p_bits[1].reveal())
print_ln("Testing. It should be: 1 = %s", p_bits[2].reveal())
print_ln("Testing. It should be: 0 = %s", p_bits[3].reveal())

############# This allows to put several elements concatenated. But you need to know in advance.


sb512 = sbits.get_type(512)
sb256 = sbits.get_type(256)
siv256 = sbitintvec.get_type(256)
siv512 = sbitintvec.get_type(512)

sha256 = Circuit('sha256')

chaining = sb256(0x6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19)

msg_buffer_1 = sb256(0b1011010110110101101101011011010110110101101101011011010110110101101101011011010110110101101101011000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
msg_buffer_2 = sb256(0b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001100000)
chain_val = sha256(siv256([msg_buffer_2]), siv256([msg_buffer_1]), sbitvec([chaining]))

chain_val.elements()[0].reveal().print_reg()
print_ln("SHA256 is %s", chain_val.elements()[0].reveal())

msg_buffer = sb512(0b10110101101101011011010110110101101101011011010110110101101101011011010110110101101101011011010110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001100000)
chain_val_2 = sha256(siv512([msg_buffer]), sbitvec([chaining]))

chain_val_2.elements()[0].reveal().print_reg()
print_ln("SHA256_2 is %s", chain_val_2.elements()[0].reveal())




##################### This puts in reversed order ######################

sb8 = sbits.get_type(9)
sb16 = sbits.get_type(32)

te01100001 = sb8(97)
te01100001_2 = sb8(98)

tbl = [te01100001,te01100001_2,te01100001,te01100001_2,te01100001,te01100001_2]

bbitss = []

for i in range(0,6):
    val = tbl[i]
    print_ln("This is uu8 %s", val.reveal())
    bbitss += val.bit_decompose()[:8]



res = sb16.bit_compose(bbitss)

print_ln("Testing. It should be: 0110000101100001 (24929) = %s", res.reveal())

Ans: 01100010 01100001 01100010 01100001 01100010 01100001
(Note that this is reversed: the last corresponds to te01100001 instead of te01100001_2)



# Parse as four 64-bit sint with 
trunc_8_0 = res.TruncPr(32,0)

sint_trunc_8_0 = sint.bit_compose(sint(trunc_8_0))

print_ln("sint of a 32 sbitint conversion. First part = %s", sint_trunc_8_0.reveal())                      

Ans: 01100010 01100001 01100010 01100001

Observe that this is reversed! the last 8 bits are the first 97 (!!)



#################

# 		Test Section

#################

"""

sb8 = sbits.get_type(9)
sb16 = sbits.get_type(32)

te01100001 = sb8(97)
te01100001_2 = sb8(98)

tbl = [te01100001,te01100001_2,te01100001,te01100001_2,te01100001,te01100001_2]

bbitss = []

for i in range(0,6):
    val = tbl[5-i]
    print_ln("This is uu8 %s", val.reveal())
    bbitss += val.bit_decompose()[:8]



res = sb16.bit_compose(bbitss)

print_ln("Testing. It should be: 0110000101100001 (24929) = %s", res.reveal())

Ans: 
01100010 01100001 01100010 01100001 01100010 01100001

Ans reverted:
01100001 01100010 01100001 01100010 01100001 01100010




# Parse as four 64-bit sint with 
trunc_8_0 = res.TruncPr(32,0)

sint_trunc_8_0 = sint.bit_compose(sint(trunc_8_0))

print_ln("sint of a 32 sbitint conversion. First part = %s", sint_trunc_8_0.reveal())                      

Ans: 
01100010 01100001 01100010 01100001

Ans reverted:
01100001 01100010 01100001 01100010


sb9 = sbits.get_type(9)
sb512 = sbits.get_type(512)

tbl = Matrix(3, 64, sb9)

for i in range(0, 3):
    tbl[i].input_from(0)



bbitss = []

for i in range(0, 64):
    val = tbl[0][63-i]
    print_ln("This is uu8 %s", val.reveal())
    bbitss += val.bit_decompose()[:8]

print_ln("The length of bbitss should be 512 = %s", len(bbitss))


test_1 = sb512.bit_compose(bbitss)

# Parse as four 64-bit sint with 
trunc_64_0 = test_1.TruncPr(32,0)

sint_trunc_64_0 = sint.bit_compose(sint(trunc_64_0))

print_ln("sint of a 256 sbitint conversion. First part = %s", sint_trunc_64_0.reveal())

01100001 01100001 01100001 01100001



print_ln("Testing. These should be equal: %s", test_1.reveal())


print_ln("Testing. It should be: 0 = %s", bbitss[0].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[1].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[2].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[3].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[4].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[5].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[6].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[7].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[8].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[9].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[10].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[11].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[12].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[13].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[14].reveal())
print_ln("Testing. It should be: 0 = %s", bbitss[15].reveal())


########### Test SHA


#si256 = sbitint.get_type(256)
siv256 = sbitintvec.get_type(256)
siv512 = sbitintvec.get_type(512)


sha256 = Circuit('sha256')

state = siv256(0x6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19)
msg = siv512(test_1)
chain_val_2 = sha256(msg, state)

chain_val_2.elements()[0].reveal().print_reg()
print_ln("SHA256 is %s", chain_val_2.elements()[0].reveal())


"""


"""
sb256 = sbits.get_type(256)
sb512 = sbits.get_type(512)
siv512 = sbitintvec.get_type(512)

sha256 = Circuit('sha256')

chaining = sb256(0x6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19)
sb32 = sbits.get_type(32)
siv256 = sbitintvec.get_type(256)


msg_buffer = sb512(0b10110101101101011011010110110101101101011011010110110101101101011011010110110101101101011011010110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001100000)
chain_val = sha256(siv512([msg_buffer]), sbitvec([chaining]))


chain_val.elements()[0].reveal().print_reg()
print_ln("SHA256 is %s", chain_val.elements()[0].reveal())





####### Written for the second issue in the github repo ########

sha256 = Circuit('sha256')

sb512 = sbits.get_type(512)
siv256 = sbitintvec.get_type(256)
siv512 = sbitintvec.get_type(512)


state = siv256(0x6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19)
secret = siv512(sb512(0x1 << 511)) # empty string case
#msg_buffer = sb512(0b10110101101101011011010110110101101101011011010110110101101101011011010110110101101101011011010110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001100000)
#secret = siv512(msg_buffer)

result = sha256(secret, state)

#result.elements()[0].reveal().print_reg()
#print_ln("SHA256 is %s", result.elements()[0].reveal())


res = result.elements()[0]

# Parse as four 64-bit sint with 
trunc_64_0 = res.TruncPr(64,0)
trunc_128_64 = res.TruncPr(128,64)
trunc_192_128 = res.TruncPr(192,128)
trunc_256_192 = res.TruncPr(256,192)

sint_trunc_64_0 = sint.bit_compose(sint(trunc_64_0))
sint_trunc_128_64 = sint.bit_compose(sint(trunc_128_64))
sint_trunc_192_128 = sint.bit_compose(sint(trunc_192_128))
sint_trunc_256_192 = sint.bit_compose(sint(trunc_256_192))


print_ln("hash[0:64] = %s", sint_trunc_64_0.reveal())
print_ln("hash[64:128] = %s", sint_trunc_128_64.reveal())
print_ln("hash[128:192] = %s", sint_trunc_192_128.reveal())
print_ln("hash[192:256] = %s", sint_trunc_256_192.reveal())




####################

# Checking Input

####################

check_first = sint.bit_compose(sint(tbl[0][0]))
print_ln("tbl[0][0] = %s", check_first.reveal())

check_first = sint.bit_compose(sint(tbl[1][0]))
print_ln("tbl[1][0] = %s", check_first.reveal())

check_first = sint.bit_compose(sint(tbl[2][0]))
print_ln("tbl[2][0] = %s", check_first.reveal())

check_first = sint.bit_compose(sint(tbl[0][1]))
print_ln("tbl[0][1] = %s", check_first.reveal())

check_first = sint.bit_compose(sint(tbl[0][2]))
print_ln("tbl[0][2] = %s", check_first.reveal())

check_first = sint.bit_compose(sint(tbl[0][10]))
print_ln("tbl[0][10] = %s", check_first.reveal())

check_first = sint.bit_compose(sint(tbl[0][60]))
print_ln("tbl[0][60] = %s", check_first.reveal())

check_first = sint.bit_compose(sint(tbl[0][127]))
print_ln("tbl[0][127] = %s", check_first.reveal())
