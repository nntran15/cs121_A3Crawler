import { React, useState } from 'react'
import axios from 'axios'
import Posting from "./Posting"

// path for search http request
const path = "http://127.0.0.1:5000/search"

const App = () => {

  const [search, setSearch] = useState("")        // search query
  const [result, setResult] = useState(null)      // results from http requests for search query
  const [time, setTime] = useState(null)          // time for getting results from query
  
  // handle search submit
  const handleSubmit = (e) => {
    e.preventDefault()
    const start = performance.now()
    axios.get(path, {
      params : {
        q : search
      }
    })
    .then((res) => {
      setResult(res.data)
      setTime(performance.now() - start)
    })
    .catch((err) => {
      console.log("error: " + err)
    }) 
  }

  // for handling enter key 
  const handleKeyDown = (e) => {
    if(e.key == 'Enter')
      handleSubmit(e)
  }

  return (
    <div>
        The best search engine ever
        <br />
        <input 
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <br />
        <br />
        {time == null ? null : `took ${time} milliseconds`}
        {
          result == null ? null : result.map((url, i) => {
            return (
              <Posting url={url} num={i} />
            )
          })
        }
        <br />  
        {result != null && result.length == 0 ? "No results found" : null}
    </div>
  )
}

export default App
