# Quantum MP-SPDZ

Integrates the usage of quantum-generated oblivious keys from QKD as Base OTs with the possibility of PSK combination. Keys are retrieved from a KMS in QKD node integrated in a QKDN.

The updates were carried out in the [`qdev`](https://github.com/diogoftm/QMP-SPDZ/tree/qdev) branch. This branch is based on [MP-SPDZ v0.4.0](https://github.com/data61/MP-SPDZ/tree/v0.4.0).

## Supported protocols

| Program | Protocol |
| --- | --- |
| `mascot-party.x` | [MASCOT](https://eprint.iacr.org/2016/505) |
| `semi-party.x` | Semi-honest version of [MASCOT](https://eprint.iacr.org/2016/505) |
| `yao-party.x` | Yao with half-gate garbling (see [Zahur et al.](https://eprint.iacr.org/2014/756.pdf) and [Guo et al.](https://eprint.iacr.org/2019/1168.pdf)) |

## Supported KMS interfaces

The current version supports the following KMS interfaces that are slightly modified for coexistence of both symmetric and oblivious keys (not in the scope of the original standards):
- [ETSI QKD 014](https://www.etsi.org/deliver/etsi_gs/QKD/001_099/014/01.01.01_60/gs_qkd014v010101p.pdf) ([Demo server/client](https://github.com/diogoftm/simulated-kms))
- [ETSI QKD 004](https://www.etsi.org/deliver/etsi_gs/QKD/001_099/004/02.01.01_60/gs_QKD004v020101p.pdf) ([Demo server/client](https://github.com/diogoftm/minimal-etsi-qkd-004))


## Installation

1. Clone this repository and checkout `qdev` branch:
    ```bash
    git clone https://github.com/diogoftm/QMP-SPDZ.git
    cd QMP-SPDZ
    git submodule update --init --recursive
    ```
2. Sent environment variables:
    Now, set the environment variables in `ENV.env`, and run:
    ```bash
    source ENV.sh
    ```
3. Make tldr: 
    ```bash
    make -j 8 tldr
    ```
    Note: This command will rename either `OTKeys_014/` or `OTKeys_004/` to `OTKeys/` based on the `KEY_REQUEST_INTERFACE`.
    To change the interface, rename the directory back to its original name.
4. Make, for example, `mascot-party.x`:
    ```bash
    make -j 8 mascot-party.x
    ```
5. Create a parties IP file:
    In this file the IP, base port and KMS application sae id need to be defined. 

    Example (SAE IDs 014 style):
    ```
    # players.txt
    127.0.0.1:1234 sae_001
    127.0.0.1:1238 sae_002
    ```

    For 004, not only the IDs of the application need to be provided, but also the key stream ID and the index of the keys to be used need to be provided for each peer. For the 014 interface with the KMS only the SAE ID need to defined. there Also, at end a 32 bit base64 encoded pre-shared key can be indicated that will be combined with the keys received from the KMS.

    Key stream information (i.e. KSID and key index) are only used for the peers, so there's no need to indicate this information for the party that will use the players file. 

    Structure for 014:
    ```
    <IP>:<PORT> <SAE_ID> - - [psk]
    <IP>:<PORT> <SAE_ID> - - [psk]
    ...
    ```

    Structure for 004:
    ```
    <IP>:<PORT> <SAE_ID> <KSID> <BASE_KEY_INDEX> [psk]
    <IP>:<PORT> <SAE_ID> <KSID> <BASE_KEY_INDEX> [psk]
    ...
    ```

    Example (SAE IDs 004 style and considering that this is the config file for party 0):
    ```
    # players.txt
    127.0.0.1:1234 qkd//app1@aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
    127.0.0.1:1238 qkd//app2@bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb 550e8400-e29b-41d4-a716-446655440000 2
    ```

    Example (SAE IDs 004 style and considering that this is the config file for party 1):
    ```
    # players.txt
    127.0.0.1:1234 qkd//app1@aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa 550e8400-e29b-41d4-a716-446655440000 2
    127.0.0.1:1238 qkd//app2@bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb
    ```
6. Compile the MPC program (e.g. crash_detection_test):
    ```bash
    ./compile.py -F 64 crash_detection_test
    ```
7. Finally, run the computation (e.g. using mascot):
    ```bash
    ./mascot-party.x -N 2 -ip players.txt -I -p 0 crash_detection_test
    ./mascot-party.x -N 2 -ip players.txt -I -p 1 crash_detection_test
    ```

    For this computation just input 3 numbers separated by a space or by a new line. 
    The first value is the flag that tells if there was a crash or not, the other two values are the $(x, y)$ coordinates. 

# More documentation

Please check the original MP-SPDZ [documentation](https://mp-spdz.readthedocs.io/en/v0.4.0/).