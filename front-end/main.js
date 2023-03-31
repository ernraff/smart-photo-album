function search()
{
	var searchBox = document.getElementsByClassName('searchbar')[0];
	console.log(searchBox.value);

	if (!searchBox.value)
	{
		alert('Please enter a valid text');
	}
	else
	{
		getPhotos(searchBox.value.trim().toLowerCase());
	}
}

function getPhotos(text)
{
	document.getElementsByClassName('searchbar')[0].value = '';

 	var sdk = apigClientFactory.newClient({apiKey: "rQkRt1wDn126eusjxpnx94279O0vKwXl90cyYNk6"});

    sdk.searchGet({ q: text, apiKey: "rQkRt1wDn126eusjxpnx94279O0vKwXl90cyYNk6"})
    	.then(function(response) {
    		console.log(response.data);
				obj = response.data;
				photo_res = obj.images;
				console.log("Show me photo results: ",photo_res);
            if (photo_res.length == 0)
            {
                alert("No images found for your search");
            }

    		var photosDiv = document.getElementById('photos_res');
    		photosDiv.innerHTML = "";

    		for (var i=0; i<photo_res.length; i++)
    		{
    			var url = 'https://er-photo-bucket.s3.amazonaws.com/' + photo_res[i];
					console.log("Show me url: ", {url});
    			photosDiv.innerHTML += "<figure><img src=" + url + " style='width:25%'></figure>"
    		}
    	}).catch(function(response){
    		console.log(response);
				alert("Sorry, not found.")
    	});
}

// function getBase64(file) {
//   return new Promise((resolve, reject) => {
//     const reader = new FileReader();
//     reader.readAsDataURL(file);
//     // reader.onload = () => resolve(reader.result)
//     reader.onload = () => {
//       let encoded = reader.result.replace(/^data:(.*;base64,)?/, '');
//       if (encoded.length % 4 > 0) {
//         encoded += '='.repeat(4 - (encoded.length % 4));
//       }
//       resolve(encoded);
//     };
//     reader.onerror = (error) => reject(error);
//   });
// }

function upload() {
  var path = (document.getElementById("uploaded_file").value).split("\\");
	console.log("Here is the path: ", path);

	customLabels = document.getElementById("custom_labels").value;
	console.log("Here are the custom labels: ", customLabels);

	var file_name = path[path.length - 1];
	console.log("The file name is: ", file_name);

	var file = document.getElementById("uploaded_file").files[0];
	console.log("Here is the file: ", file);

	if (customLabels.length != 0) {
			var headers = {
					'Content-Type': file.type,
					'x-amz-meta-customlabels': customLabels
			};
	} else {
			var headers = {
					'Content-Type': file.type,
			};
	};

	console.log("The headers are: ", headers);

	console.log(file.name.split('.')[0]);

	url = "https://symqbsrya1.execute-api.us-east-1.amazonaws.com/alpha/upload/er-photo-bucket/" + file.name;

	// var params = {
	// 	Bucket: 'er-photo-bucket',
	// 	key: file_name,
	// 	'x-amz-meta-customlabels': customLabels
	// };
	// var body = file;
	// var additionalParams = {};

	axios.put(url, file, { headers: headers }).then(response => {
        console.log(response)
        alert("Image uploaded: " + file.name);
    }).catch(function(result) {
        console.log("result", result);
    });

  // const reader = new FileReader();
	//
  // var encoded_image = getBase64(file).then((data) => {
  //   console.log("Data:", data);
	//
  // var sdk = apigClientFactory.newClient({apiKey: "rQkRt1wDn126eusjxpnx94279O0vKwXl90cyYNk6"});

	//
  // var file_type = file.type + ';base64';
  // console.log("File Type below:");
  // console.log(file_type);

  //   var params = {
  //     key: file.name,
  //     bucket: 'er-photo-bucket',
  //     'x-amz-meta-customlabels': custom_labels.value
  //   };
  //   console.log("The labels are: ",custom_labels.value)
  //   var additionalParams = {
	// 		headers: {
	// 			'Accept': 'image/*',
	// 			'Content-Type': file_type
	// 		}
	// 	};
//     sdk
//       .uploadPut(params, body, additionalParams)
//       .then(function (res) {
//         if (res.status == 200) {
// 					alert('Image uploaded succesfully!');
//         }
//       });
//   // });
}

window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition

function interpretVoice()
{
    if ('SpeechRecognition' in window) {
        console.log("SpeechRecognition is Working");
    } else {
        console.log("SpeechRecognition is Not Working");
    }

    var searchBox = document.getElementsByClassName('searchbar')[0];
    const recognition = new window.SpeechRecognition();

    mic = document.getElementById("switch");

    if (mic.innerHTML == "micOn") {
        recognition.start();
    } else if (mic.innerHTML == "micOff"){
        recognition.stop();
    }

    console.log("reached")

    recognition.addEventListener("start", function() {
        console.log("reached")

        mic.innerHTML = "micOff";
        console.log("Recording.....");
    });

    recognition.addEventListener("end", function() {
        console.log("Stopping recording.");
        mic.innerHTML = "micOn";
    });

    recognition.addEventListener("result", resultOfSpeechRecognition);
    function resultOfSpeechRecognition(event) {
        const current = event.resultIndex;
        transcript = event.results[current][0].transcript;
        searchBox.value = transcript;
        console.log("transcript : ", transcript)
    }
}
