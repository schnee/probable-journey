import tensorflow as tf
import tensorflow_hub as hub

# Load the Universal Sentence Encoder model
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

# Define the two sentences
sentence1 = "evil motherfucker"
sentence2 = "Tom Hanks"
sentence3 = "Ron DeSantis"

# Embed the sentences
embedding1 = embed([sentence1])
embedding2 = embed([sentence2])
embedding3 = embed([sentence3])

# Calculate the similarity using cosine similarity
similarity = tf.keras.losses.cosine_similarity(embedding1, embedding2).numpy()[0]

similarity2 = tf.keras.losses.cosine_similarity(embedding1, embedding3).numpy()[0]

print(f"The similarity between '{sentence1}' and '{sentence2}' is: {similarity}")
print(f"The similarity between '{sentence1}' and '{sentence3}' is: {similarity2}")