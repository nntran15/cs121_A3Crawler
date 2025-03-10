import {React, useState, useEffect} from "react";
import axios from 'axios'

const path = "http://127.0.0.1:5000/summary"


const Posting = ({ num, url }) => {

  const [summary, setSummary] = useState(null)
  const [clicked, setClicked] = useState(false)

  useEffect(() => {
    setSummary(null)
    setClicked(false)
  }, [url]);

  const handleAISubmit = (e) => {
    e.preventDefault()
    if(clicked) return

    setClicked(true)
    axios.get(path, {
      params : {
        q : url
      }
    })
    .then((res) => {
      setSummary(res.data)
    })
    .catch((err) => {
      console.log("error: " + err)
    }) 
  }

  return (
    <div>
      <br />
      <a href={url}>{`${num + 1}. ${url}`}</a>
      <br />
      {(summary == null) 
        ? <button onClick={handleAISubmit}>{clicked ? "Loading" : "AI Summary"}</button>
        : <div>
            {summary}
            <br />
          </div>
      }
    </div>
  )
}

export default Posting;
