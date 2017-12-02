library(mongolite)
library(spacyr)
library(tidyverse)
library(tidytext)
library(tm)
library(topicmodels)
library(dplyr)


tidyData <- function (pythonpath, type, pos_array, additionalStopwords) {
  my_collection = mongo(collection = "articles", db = "projectfinal_db")
  data <- my_collection$find(paste0('{"type":"',type,'"}'),
                             fields = '{"_id":0, "link":1, "refinedtext":1}')
  data_asfact <- data$refinedtext
  names(data_asfact) <- data$link
  parsedtxt <- spacy_parse(data_asfact)
  topic_parsed <- filter(parsedtxt, pos %in% pos_array)
  topic_parsed <-rename(topic_parsed, word = token)

  topic_parsed<- topic_parsed %>%
    anti_join(stop_words)
  
 topic_parsed<- topic_parsed %>%
    anti_join(additionalStopwords)
  
  topic_parsed <- filter(topic_parsed, !grepl("[^0-9A-Za-z///']",word))
  text <- topic_parsed %>%
    group_by(doc_id) %>%
    summarise(text=paste(word,collapse=' '))
  
  return(text)
}

spacy_initialize(python_executable=pythonpath)

pos_array = c("NOUN")
entertainment_stops <- data.frame( word=c("will", "image"))
sports_stops <- data.frame(word= c("game", "season", "play", "time", "coach", "week", "team", "day"))
data_text <- tidyData('/home/parth/tensorflow/bin/python', "Sports", pos_array, sports_stops)

docs <- Corpus(VectorSource(data_text$text))
docs <-tm_map(docs,content_transformer(tolower))
dtm <- DocumentTermMatrix(docs)
rownames(dtm) <- data_text$doc_id
freq <- colSums(as.matrix(dtm))
lda_res <- LDA(dtm, k=7, control = list(seed = 1234))
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

ap_documents <- tidy(lda_res, matrix = "gamma")
ap_documents

g <- ap_documents %>%
  group_by(topic) %>%
  filter(gamma > 0.99) %>%
  ggplot() +
  geom_bar(mapping = aes(x=topic))


