category <- c("Politics", "Entertainment", "Sports")

k <-

ui <- fluidPage(
  # Application title
  titlePanel("Word Cloud"),

  sidebarLayout(
    # Sidebar with a slider and selection inputs
    sidebarPanel(
      selectInput("selection", "Category:",
                  choices = category),
      actionButton("update", "Change"),
      hr(),


      sliderInput("k",
                  "Number of Topics:",
                  min = 1,  max = 10, value = 7)


    ),

    # Show Word Cloud
    mainPanel(
      plotOutput("plot")
    )
  )
)

server <- function(input, output, session) {
  # Define a reactive expression for the document term matrix
  terms <- reactive({
    # Change when the "update" button is pressed...
    input$update
    # ...but not for anything else
    isolate({
      withProgress({
        setProgress(message = "Processing corpus...")
        getTermMatrix(input$selection)
      })
    })
  })

  # Make the wordcloud drawing predictable during a session
  wordcloud_rep <- repeatable(wordcloud)

  output$plot <- renderPlot({
    v <- terms()
    wordcloud_rep(names(v), v, scale=c(4,0.5),
                  min.freq = input$freq, max.words=input$max,
                  colors=brewer.pal(8, "Dark2"))
  })
}

runApp(list(ui=ui, server=server))
