from VRPPD import *

instance_folder_path = "training_data/0b220d8f-ba16-4848-86ef-b446ef436fce"

prob = VRPPD()
prob.read(instance_folder_path)

prob.mip_solve()

print(prob)