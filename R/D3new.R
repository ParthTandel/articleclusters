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
library(rjson)






tidyData <- function (pythonpath, type, pos_array, additionalStopwords) {
  my_collection = mongo(collection = "articles", db = "projectfinal_db")
  data <- my_collection$find(paste0('{"type":"',type,'", "date" : "17-11-21"}'),
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
category <- c("Politics", "Entertainment", "Sports")


ui <- fluidPage(
    titlePanel("Topic Modelling with LDA"),
    sidebarLayout(
      sidebarPanel(width = 4,
        selectInput("selection", "Category:",
                    choices = category),
        hr(),
        sliderInput("k",
                    "Number of Topics:",
                    min = 1,  max = 10, value = 7),

        actionButton("run", "Create Clusters!")

      ),
      mainPanel(
        fluidPage(column(width=3, offset=5,
                         conditionalPanel(condition="$('html').hasClass('shiny-busy')",
                                          p("Pulling from API..")
                         )
                         )),
        fluidPage(column(width=12,
                         conditionalPanel(condition="!$('html').hasClass('shiny-busy')",
                                          h3(textOutput("Clusters")),
                                          tags$head(tags$link(rel = "stylesheet", type = "text/css", href = "http://localhost:8000/style.css")),
                                          tags$script(src="https://d3js.org/d3.v3.min.js"),
                                              tags$script(src="http://localhost:8000/d3script.js"),
                                          tags$div(id="div_tree")
                        )
                    )
                )
      )
    )
  )


server <- function(input, output, session) {
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

  observeEvent(input$run,{


    lda_res <- processed_data()
    ap_documents <- tidy(lda_res, matrix = "gamma")
    ap_documents <- ap_documents %>%
     group_by(topic) %>%
     filter(gamma > 0.995)


    ap_topics <- tidy(lda_res, matrix = "beta")
    ap_top_terms <- ap_topics %>%
     group_by(topic) %>%
     top_n(9, beta) %>%
     ungroup() %>%
     arrange(topic, -beta)

    print("data sent")
    session$sendCustomMessage(type="jsondata", toJSON(list(ap_documents,ap_top_terms)))

  })
}

runApp(list(ui=ui, server=server))
