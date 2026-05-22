namespace JordanQuillen

structure SquareZeroExtensionShape where
  baseDimension : Nat
  moduleDimension : Nat

def SquareZeroExtensionShape.totalDimension
    (shape : SquareZeroExtensionShape) : Nat :=
  shape.baseDimension + shape.moduleDimension

end JordanQuillen
