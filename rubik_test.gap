# 2x2x2 Rubik's Cube group tests
# --- Generators on 24 "stickers" (clockwise when looking at that face) ---
R := (2,19,22,10)(4,17,24,12)(13,14,16,15);;
U := (1,2,4,3)(5,17,13,9)(6,18,14,10);;
F := (3, 13,22,8)(4,15,21,6)(9,10,12,11);;

cube_2x2x2 := Group(R, U, F);;
Print("Order(cube_2x2x2) = ", Order(cube_2x2x2), "\n");; # Should be 3674160


# Check for Lemma 9
RU := R * U;;
subRU := Group(RU);;
Print("Order(subRU) = ", Order(subRU), "\n");; # Should be 15


# Check for Lemma 12
# Helper: check evenness of a permutation
IsEven := g -> SignPerm(g) = 1;

# Cycle class [g] for EVEN g, per Definition 8 / Lemma 9 discussion:
#   [g] = { g*(RU)^k*R^sigma : 0<=k<15, sigma in {0,1} }
CycleClassEven := function(g)
  local k, L;
  if not IsEven(g) then
    Error("CycleClassEven expects an even element");
  fi;
  L := [];
  for k in [0..14] do
    Add(L, g * (RU^k));         # sigma = 0
    Add(L, g * (RU^k) * R);     # sigma = 1
  od;
  return Set(L);               # make order/copies irrelevant for equality tests
end;

UU := U^-1 * U^-1;                  # U^{-1}U^{-1} = U^{-2}, this is even
UpRp := U^-1 * R^-1;                  

base := CycleClassEven(UU);

Print("k values where [U^{-2}] = [(U^{-1}R^{-1})^k U^{-2}]:\n");
for k in [0..14] do
  if base = CycleClassEven((UpRp^k) * UU) then
    Print(k, " ");
  fi;
od;
Print("\nExpected: 0 5 10\n");

# Section 5
R_U_subgroup := Group(R, U);;
Print("Order(R_U_subgroup) = ", Order(R_U_subgroup), "\n"); # Should be 29160

# --- Lemma 22 check: deg_{Q_R}(<R,U>) = 90 ---
Print("Index(<R, U, F>,<R, U>) = ", Index(cube_2x2x2,R_U_subgroup), "\n");;   # should be 126

# Vertices of Q_R are LEFT cosets gH
cosets := LeftCosets(cube_2x2x2, R_U_subgroup);;
Print("|Q_R| = ", Length(cosets), "\n");;    # should be 126

# Precompute representatives so we can locate cosets quickly
reps := List(cosets, Representative);;

# Map x in cube_2x2x2 to the index i such that x is in reps[i]*R_U_subgroup (i.e., xR_U_subgroup is that coset)
CosetIndex := function(x)
  local i;
  for i in [1..Length(reps)] do
    # x in reps[i]*R_U_subgroup  <=>  reps[i]^-1 * x in R_U_subgroup
    if (reps[i]^-1 * x) in R_U_subgroup then
      return i;
    fi;
  od;
  Error("CosetIndex: could not locate coset for given element");
end;

# Identify the vertex R_U_subgroup itself (the coset containing the identity)
id := Identity(cube_2x2x2);;
idIdx := CosetIndex(id);;

Finv := F^-1;;

# --- Definition of adjacency in Q_R specialized to A = H ---
# B is adjacent to R_U_subgroup iff:
#  - there is some EVEN a in R_U_subgroup with a*F^{+-1} landing in B (odd vertex in B),
#  - and some ODD  a in R_U_subgroup with a*F^{+-1} landing in B (even vertex in B).
#
# So compute:
#   evenHit = { (a*F^{+-1})R_U_subgroup : a in R_U_subgroup even }
#   oddHit  = { (a*F^{+-1})R_U_subgroup : a in R_U_subgroup odd  }
# Neighbors are Intersection(evenHit, oddHit), excluding R_U_subgroup itself.

evenHit := [];;
oddHit  := [];;

for a in Elements(R_U_subgroup) do
  if IsEven(a) then
    Add(evenHit, CosetIndex(a * F));
    Add(evenHit, CosetIndex(a * Finv));
  else
    Add(oddHit,  CosetIndex(a * F));
    Add(oddHit,  CosetIndex(a * Finv));
  fi;
od;

evenHit := Set(evenHit);;
oddHit  := Set(oddHit);;

neighbors := Intersection(evenHit, oddHit);;

# Remove self if it appears (it *shouldn't* be adjacent to itself)
if idIdx in neighbors then
  RemoveSet(neighbors, idIdx);
fi;

Print("deg_{Q_R}(<R,U>) = ", Length(neighbors), "\n");;
Print("Expected: 90\n");