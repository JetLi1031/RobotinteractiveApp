var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
var SpeechGrammarList = SpeechGrammarList || webkitSpeechGrammarList;
var SpeechRecognitionEvent = SpeechRecognitionEvent || webkitSpeechRecognitionEvent;

var phrases = [
  'forward',
  'backward',
  'left',
  'right',
  'stop',
];
var latched = true;
var phrasePara = document.querySelector('.phrase');
var resultPara = document.querySelector('.result');
var diagnosticPara = document.querySelector('.output');

var testBtn = document.querySelector('.start');
var testBtn2 = document.querySelector('.stop');

testBtn2.disabled=true;

function testSpeech() {
 
  testBtn.disabled = true;
  testBtn.textContent = 'Listening in progress';
  testBtn2.disabled=false;
  testBtn2.textContent='Stop if pressed';

  // var phrase = phrases[randomPhrase()];
  // // To ensure case consistency while checking with the returned output text
  // phrase = phrase.toLowerCase();
  // phrasePara.textContent = phrase;
  // resultPara.textContent = 'Right or wrong?';
  // resultPara.style.background = 'rgba(0,0,0,0.2)';
  // diagnosticPara.textContent = '...diagnostic messages';

  var grammar = '#JSGF V1.0; grammar phrase; public <phrase> = ' +  phrases.join(' | ') +';';
  var recognition = new SpeechRecognition();
  var speechRecognitionList = new SpeechGrammarList();
  speechRecognitionList.addFromString(grammar, 1);
  recognition.grammars = speechRecognitionList;
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  

  recognition.start();

  recognition.onresult = function(event) {
    if(latched == false){
      return;
    }
    var speechResult = event.results[0][0].transcript.toLowerCase();
    //console.log(Array.from(event.results));
    diagnosticPara.textContent = 'Speech received: ' + speechResult + '.';
    // if(speechResult === phrase) {
    //   resultPara.textContent = 'I heard the correct phrase!';
    //   resultPara.style.background = 'lime';
    // } else {
    //   resultPara.textContent = 'That didn\'t sound right.';
    //   resultPara.style.background = 'red';
    // }

    phrases.forEach((element,index) => {
    if (speechResult.includes(element)){
    switch (phrases[index]){
    	case "forward":
    		rosbrige_publishconverted("tounchstart","Up");
        console.log("Up");
    		break;
    	case "backward":
    		rosbrige_publishconverted("tounchstart","Down");
        console.log("Down");
    		break;
    	case "left":
    		rosbrige_publishconverted("tounchstart","Left")
        // console.log("Left");
    		break;
    	case "right":
    		rosbrige_publishconverted("tounchstart","Right");
        break;
    	case "stop":
    		["Up","Down","Left","Right"].forEach(element => {rosbrige_publishconverted("tounchend",element);})
        console.log("Right");
    		break;
    }
    }
  })

    console.log('Confidence: ' + event.results[0][0].confidence);
  }

  
  
  recognition.onend = function(event) {
      //Fired when the speech recognition service has disconnected.
      if(latched == true){
      recognition.start();
      console.log("latching");
      } 
      
      console.log('SpeechRecognition.onend');
  }
  
  recognition.onnomatch = function(event) {
      //Fired when the speech recognition service returns a final result with no significant recognition. This may involve some degree of recognition, which doesn't meet or exceed the confidence threshold.
      console.log('SpeechRecognition.onnomatch');
  }
  

  recognition.onstart = function(event) {
      //Fired when the speech recognition service has begun listening to incoming audio with intent to recognize grammars associated with the current SpeechRecognition.
      latched = true;
      console.log('SpeechRecognition.onstart');
  }
}

testBtn.addEventListener('click', testSpeech);
testBtn2.addEventListener('click', function(){
latched = false;
testBtn2.disabled=true;
testBtn2.textContent= "Stop command";
testBtn.disabled = false;
testBtn.textContent= "Start command";
["Up","Down","Left","Right"].forEach(element => {rosbrige_publishconverted("tounchend",element);})

});

