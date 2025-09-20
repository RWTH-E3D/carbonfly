height = 0.0 if height is None or height <= 0 else height
weight = 0.0 if weight is None or weight <= 0 else weight

# BSA (m^2) / height (cm) /  weight (kg)
BSA = 0.007184 * (height ** 0.725) * (weight ** 0.425)
