import {React, useState, useEffect} from "react";
import axios from 'axios'

// path for summary request
const path = "/summary"

const Posting = ({ num, url }) => {

  const [summary, setSummary] = useState(null)      // AI summary to be displayed
  const [clicked, setClicked] = useState(false)     // boolean variable for if button was clicked

  // react doesnt default reset these variables on rerender with different url??
  // manual reset
  useEffect(() => {
    setSummary(null)
    setClicked(false)
  }, [url]);

  // handle ai summary buttom submit
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

  // jsx
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
