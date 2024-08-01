import tensrflow_datasets as tfds

#Smaller dataset
dataset, info = tfds.load("c4/webtextlike", split="train", with_info=True)
print(info)