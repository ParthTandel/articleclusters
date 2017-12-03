library(mongolite)
library(spacyr)
library(tidyverse)
library(tidytext)
library(tm)
library(topicmodels)
library(dplyr)
library(gridExtra)
library(ggrepel)
library(wordcloud)






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


  return(topic_parsed)
}

generate_Clusters <- function(data_text, kparam) {

  docs <- Corpus(VectorSource(data_text$text))
  docs <-tm_map(docs,content_transformer(tolower))
  dtm <- DocumentTermMatrix(docs)
  rownames(dtm) <- data_text$doc_id
  freq <- colSums(as.matrix(dtm))
  lda_res <- LDA(dtm, k= kparam, control = list(seed = 1234))
  return(lda_res)
}

spacy_initialize(python_executable='/home/parth/tensorflow/bin/python')

# pos_array = c("NOUN")
# entertainment_stops <- data.frame( word=c("will", "image"))
# sports_stops <- data.frame(word= c("game", "season", "play", "time",
#                                    "coach", "week", "team", "day",
#                                    "photos", "games", "sports", "night",
#                                    "times", "story", "newsletter", "sport",
#                                    "player", "players", "photo", "half",
#                                    "teams", "ball","hall"))
# topic_parsed <- tidyData('/home/parth/tensorflow/bin/python', "Sports", pos_array, sports_stops)
# data_text <- topic_parsed %>%
#   group_by(doc_id) %>%
#   summarise(text=paste(word,collapse=' '))
#
# ap_topics <- generate_Clusters(data_text, 8)
#
#
#
# ap_top_terms <- ap_topics %>%
#   group_by(topic) %>%
#   top_n(10, beta) %>%
#   ungroup() %>%
#   arrange(topic, -beta)
#
#
# ap_top_terms %>%
#   mutate(term = reorder(term, beta)) %>%
#   ggplot(aes(term, beta, fill = factor(topic))) +
#   geom_col(show.legend = FALSE) +
#   facet_wrap(~ topic, scales = "free") +
#   coord_flip()
#
# ap_documents <- tidy(lda_res, matrix = "gamma")
# ap_documents
#
# g <- ap_documents %>%
#   group_by(topic) %>%
#   filter(gamma > 0.99) %>%
#   ggplot() +
#   geom_bar(mapping = aes(x=topic))
#

category <- c("Politics", "Entertainment", "Sports")

ui <- fluidPage(
    # Application title
    titlePanel("Topic Modelling with LDA"),

    sidebarLayout(
      # Sidebar with a slider and selection inputs
      sidebarPanel(width = 4,
        selectInput("selection", "Category:",
                    choices = category),
        hr(),


        sliderInput("k",
                    "Number of Topics:",
                    min = 1,  max = 10, value = 7),

        uiOutput("slider"),

        # sliderInput("topic_sec",
        #             "Topic selected:",
        #             min = 1,  max = 10, value = 7),

        sliderInput("numword",
                  "Number of words",
                  min = 5,  max = 50, value = 10)
      ),
      plotOutput("plot", click = "plot_click")

      # conditionalPanel("values.show",
      #     plotOutput("plot", click = "plot_click")
      # )

    )
  )


server <- function(input, output, session) {
#
#   values <- reactiveValues()
#   values$show <- FALSE
#

  output$slider <- renderUI({
    sliderInput(inputId = "topic_sec", label = "Current topic", min = 0, max = input$k, value = 1, step = 1)
  })

  processed_data <- reactive({

    pos_array = c("NOUN")
    entertainment_stops <- data.frame( word=c("will", "image"))
    sports_stops <- data.frame(word= c("game", "season", "play", "time",
                                       "coach", "week", "team", "day",
                                       "photos", "games", "sports", "night",
                                       "times", "story", "newsletter", "sport",
                                       "player", "players", "photo", "half",
                                       "teams", "ball","hall"))
    print("topic started")
    topic_parsed <- tidyData('/home/parth/tensorflow/bin/python', input$selection, pos_array, sports_stops)
    print("spacy parsed")

    data_text <- topic_parsed %>%
      group_by(doc_id) %>%
      summarise(text=paste(word,collapse=' '))

    lda_res <- generate_Clusters(data_text, input$k)
    return(lda_res)
  })

  # wordcloud_rep <- repeatable(wordcloud)

  output$plot <- renderPlot({

    lda_res <- processed_data()
    wordcloud_rep <- repeatable(wordcloud)
    ap_topics <- tidy(lda_res, matrix = "beta")

    ap_top_terms <- ap_topics %>%
      filter(topic == input$topic_sec) %>%
      top_n(input$numword, beta) %>%
      ungroup() %>%
      arrange(topic, -beta)


    set.seed(1234)
    wordcloud(words = ap_top_terms$term, freq = 1000*ap_top_terms$beta, min.freq = 1,
          max.words=200, random.order=FALSE, rot.per=0.35,
          colors=brewer.pal(8, "Dark2"))

    # ap_top_terms %>%
    #   mutate(term = reorder(term, beta)) %>%
    #   ggplot(aes(term, beta, fill = factor(topic))) +
    #   geom_col(show.legend = FALSE) +
    #   facet_wrap(~ topic, scales = "free", nrow = NULL, ncol = 2) +
    #   coord_flip() +
    #   theme(axis.title.y = element_text(size=18,face="bold"),
    #         axis.text.x = element_text(size=18,face="bold"),
    #         axis.text.y = element_text(size=18,face="bold"),
    #         axis.title.x = element_text(size=18,face="bold"))

    }, height = 900, width = 800)

}

runApp(list(ui=ui, server=server))
