package main

import (
    "os"
    "log"
    "net/url"
    "strings"
    "net/http"

    "github.com/PuerkitoBio/goquery"
)

func main(){
  var err error

  URL, _ := url.ParseRequestURI(os.Args[1])

  home, _ := os.UserHomeDir()

  path := strings.Split(URL.Path, "/")
  _, err = os.Stat(home + "/" + path[2]+ "/" + path[4])

  if os.IsNotExist(err){
    os.MkdirAll(home + "/" + path[2], 0755)
    f, _ := os.OpenFile(home + "/" + path[2]+ "/" + path[4], os.O_CREATE|os.O_WRONLY, 0755)
    defer f.Close()
    res, err := http.Get(os.Args[1])
    if err != nil {
      log.Fatal(err)
    }
    defer res.Body.Close()
    doc, err := goquery.NewDocumentFromReader(res.Body)

    doc.Find(".problem-statement").Each(func(i int, s *goquery.Selection){
      prob := s.Text()
      f.WriteString(prob)
    })
  }
}
