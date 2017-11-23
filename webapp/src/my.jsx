import React from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import Progress from "react-progressbar";

class Counter extends React.Component {

    constructor(props){
      super(props);
      this.state = {
        objects: 0,
        url: '/data/',
      };
    }

   get_data() {
     axios.get(this.state.url)
       .then(res => {
         console.log(res);
         this.setState({ objects: res.data.length})
       });
   }


  componentDidMount() {
   var intervalId = setInterval(this.get_data.bind(this), 500);
   this.setState({intervalId: intervalId});
 }
   componentWillUnmount() {
     clearInterval(this.state.intervalId);
   }

    render() {
        return <div>
           <div>Already {this.state.objects} objects</div>
           <Progress completed={100.0 * this.state.objects/600} />
           </div>;
    }
}

ReactDOM.render(<div>
  <Counter/>
  </div>,
document.getElementById('root'));
