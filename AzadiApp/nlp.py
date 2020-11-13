# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import PorterStemmer, WordNetLemmatizer
# import nltk
# from nltk.corpus import wordnet
# import pyaudio
# import speech_recognition as sr

# syns = wordnet.synsets("program")
# r = sr.Recognizer()
# ps = PorterStemmer()
# lemmatizer = WordNetLemmatizer()

# def detect_problem():

#     def rem_punct(my_str):
#         punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
#         no_punct = ""
#         for char in my_str:
#             if char not in punctuations:
#                 no_punct = no_punct + char
#         no_punct = no_punct.lower()
#         return no_punct

#     print("Speak")
#     with sr.Microphone() as source:
#         audio_data = r.record(source, duration=5)
#         print("Recognizing")
#         text = r.recognize_google(audio_data)
#         example_sentence = text

#     # print(example_sentence)

#     example_sentence = rem_punct(example_sentence)
#     stop_words = set(stopwords.words("english"))
#     words = word_tokenize(example_sentence)

#     filtered_sentence = [w for w in words if not w in stop_words]

#     lem_sentence = []
#     for w in filtered_sentence:
#         lem_sentence.append(lemmatizer.lemmatize(w))

#     distress = ["emergency", "ambulance", "pain", "police", "attacker", "danger", "fire"]

#     pos = []
#     problem_list = []
#     pos = nltk.pos_tag(lem_sentence)
#     # print(pos)
#     for k, v in pos:
#         if v == "NN" or v == "NNS":
#             max_score = 0
#             try:
#                 for d in distress:
#                     w2 = wordnet.synset("{}.n.01".format(d))
#                     w1 = wordnet.synset("{}.n.01".format(k))
#                     sim = w1.wup_similarity(w2)
#                     # print(sim)
#                     if sim > max_score:
#                         max_score = sim
#                         problem = d
#                         word = k
#                 problem_list.append(problem)
#                 # print(problem, word, sim)
#             except:
#                 pass
#     solution = []
#     for p in problem_list:
#         index = distress.index(p)
#         if index in range(0,3):
#             solution.append("ambulance")
#         elif index in range(3,6):
#             solution.append("police")
#         else:
#             solution.append("firebrigade")

#     return solution

# print(detect_problem())