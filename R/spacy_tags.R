library(mongolite)
library(spacyr)
library(tidyverse)
library(tidytext)
library(tm)
library(topicmodels)
library(dplyr)


spacy_initialize(python_executable='/home/parth/tensorflow/bin/python')
my_collection = mongo(collection = "articles", db = "projectfinal_db")
data <- my_collection$find('{"type":"Politics"}',fields = '{"_id":0, "link":1, "refinedtext":1}')

# parsedtxt <- spacy_parse(data$refinedtext)
# topic_parsed <- filter(parsedtxt,(pos == "PROPN" |
#                        pos == "VERB" )&(
#                        entity == "PERSON_B" |
#                        entity == "PERSON_I" |
#                        entity == "DATE_B" |
#                        entity == "GPE_B" |
#                        entity == "ORG_B" |
#                        entity == "ORG_I"))
#
# topic_parsed <-rename(topic_parsed, word = token)
# topic_parsed<- topic_parsed %>%
#    anti_join(stop_words)
#
#
# data_text <- topic_parsed %>%
#   group_by(doc_id) %>%
#   summarise(text=paste(word,collapse=' '))

docs <- Corpus(VectorSource(data$refinedtext))
docs <-tm_map(docs,content_transformer(tolower))
dtm <- DocumentTermMatrix(docs)
rownames(dtm) <- data$link
freq <- colSums(as.matrix(dtm))
lda_res <- LDA(dtm, k=6, control = list(seed = 1234))
lda_res

ap_topics <- tidy(lda_res, matrix = "beta")
ap_topics


ap_top_terms <- ap_topics %>%
  group_by(topic) %>%
  top_n(10, beta) %>%
  ungroup() %>%
  arrange(topic, -beta)


ap_top_terms %>%
  mutate(term = reorder(term, beta)) %>%
  ggplot(aes(term, beta, fill = factor(topic))) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~ topic, scales = "free") +
  coord_flip()

g <- ap_documents %>%
  group_by(topic) %>%
  filter(gamma > 0.9) %>%
  ggplot() +
  geom_bar(mapping = aes(x=topic))
