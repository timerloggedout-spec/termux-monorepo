// Jazz 3:2 off-beat study — independent polyphonic roles.
stack(
  s("bd ~ ~ bd ~ ~").fast(2).gain(0.82),
  s("~ sn ~ ~ sn ~").fast(2).gain(0.62),
  s("hh*8").gain(0.24),
  note("c2 ~ g2 ~").slow(2).s("sawtooth").gain(0.42),
  note("c4 eb4 g4 bb4").fast(3/2).s("triangle").gain(0.36),
  note("g4 ~ eb4 d4").slow(3).s("sine").gain(0.28)
)
