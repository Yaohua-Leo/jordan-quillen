import JordanQuillen.Basic

namespace JordanQuillen

structure JordanAlgebra (A : Type u) where
  mul : A -> A -> A
  commutative : forall x y : A, mul x y = mul y x

end JordanQuillen
