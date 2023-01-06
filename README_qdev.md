## Note

This `qdev` branch starts from the commit `565c364cd4204a8d697c7ab3d235774a15ecb29e`.

It integrates OTKeys module from [here]()



Steps:

1. Change `BaseOT::exec_base(int my_num, int other_player, bool new_receiver_inputs)` definition to include `my_num` and `other_player` indexes.
2. The files affected by this change:
- `OTMachine.cpp`.
- `OTTripleSetup.cpp`.
- `OTExtensionWithMatrix.cpp`.
- `OTMultiplier.hpp`.

To work with MASCOT we only call `OTTripleSetup.cpp`. The other files are not prepared to work with OTKeys modules. Therefore, in the meantime and to avoid future errors, the program breaks whenever one of the following is called: `OTMachine.cpp`, `OTExtensionWithMatrix.cpp` or `OTMultiplier.hpp`.







