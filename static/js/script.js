 // 🌍 Change language placeholders
function changeLanguage(){

    let lang = document.getElementById("lang").value;

    let labels = {
        en: ["Nitrogen (0-140)","Phosphorus (5-145)","Potassium (5-205)","Temperature (0-50)","Humidity (0-100)","pH (0-14)","Rainfall (0-300)"],
        te: ["నైట్రోజన్ (0-140)","ఫాస్పరస్ (5-145)","పొటాషియం (5-205)","ఉష్ణోగ్రత (0-50)","తేమ (0-100)","పీహెచ్ (0-14)","వర్షపాతం (0-300)"],
        hi: ["नाइट्रोजन (0-140)","फॉस्फोरस (5-145)","पोटैशियम (5-205)","तापमान (0-50)","नमी (0-100)","पीएच (0-14)","वर्षा (0-300)"]
    };

    let fields = ["n","p","k","temp","humidity","ph","rain"];

    fields.forEach((id,i)=>{
        document.getElementById(id).placeholder = labels[lang][i];
    });
}


// ✅ Validate inputs (manual mode)
function validateInputs(data){

    if(isNaN(data.N) || data.N < 0 || data.N > 140) return "Nitrogen must be 0-140";
    if(isNaN(data.P) || data.P < 5 || data.P > 145) return "Phosphorus must be 5-145";
    if(isNaN(data.K) || data.K < 5 || data.K > 205) return "Potassium must be 5-205";
    if(isNaN(data.temperature) || data.temperature < 0 || data.temperature > 50) return "Temperature must be 0-50";
    if(isNaN(data.humidity) || data.humidity < 0 || data.humidity > 100) return "Humidity must be 0-100";
    if(isNaN(data.ph) || data.ph < 0 || data.ph > 14) return "pH must be 0-14";
    if(isNaN(data.rainfall) || data.rainfall < 0 || data.rainfall > 300) return "Rainfall must be 0-300";

    return null;
}


// 📍 GPS LOCATION FUNCTION
function getLocation(){

    alert("Fetching location... 🌍");

    if(navigator.geolocation){

        navigator.geolocation.getCurrentPosition(
            position => {

                let lat = position.coords.latitude;
                let lon = position.coords.longitude;

                sendData({
                    lat: lat,
                    lon: lon
                });

            },
            () => alert("Location access denied ❌")
        );

    } else {
        alert("Geolocation not supported ❌");
    }
}


// 🚀 MAIN FUNCTION
function predictCrop(){

    let place = document.getElementById("place").value.trim();
    let lang = document.getElementById("lang").value;

    let data;

    // 🌍 PLACE MODE
    if(place){
        data = {
            place: place,
            lang: lang
        };
    }

    // ✍️ MANUAL MODE
    else{

        data = {
            N: parseFloat(n.value),
            P: parseFloat(p.value),
            K: parseFloat(k.value),
            temperature: parseFloat(temp.value),
            humidity: parseFloat(humidity.value),
            ph: parseFloat(ph.value),
            rainfall: parseFloat(rain.value),
            lang: lang
        };

        let error = validateInputs(data);

        if(error){
            alert(error);
            return;
        }
    }

    sendData(data);
}


// 🔥 COMMON API CALL FUNCTION
function sendData(data){

    fetch('/predict',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(data)
    })
    .then(async res => {

        let text = await res.text();

        try{
            return JSON.parse(text);
        }catch{
            throw new Error("Server error (invalid response)");
        }

    })
    .then(res=>{

        if(res.error){
            alert(res.error);
            return;
        }

        // 📍 Location + Weather info
        let info = `
        <div style="
            margin-bottom:12px;
            padding:10px;
            background:#eef9f1;
            border-radius:10px;
            font-size:15px;
        ">
            📍 <b>${res.location}</b><br>
            🌡 Temp: ${res.temperature}°C | 💧 Humidity: ${res.humidity}%
        </div>
        `;

        let html="";

        res.top.forEach((c,i)=>{

            let color = i==0 ? "#2ecc71" : i==1 ? "#f39c12" : "#e74c3c";

            html += `
            <div style="
                padding:12px;
                margin:10px 0;
                border-radius:10px;
                background:#f5f5f5;
                border-left:5px solid ${color};
                font-size:16px;
            ">
                🌾 <b>${c.name}</b><br>
                <small>${c.prob}% probability</small>
            </div>`;
        });

        document.getElementById("output").innerHTML = info + html;
        document.getElementById("fertilizer").innerText = res.fertilizer;

    })
    .catch(err=>{
        alert("Error: " + err.message);
    });
}


// 🔄 Auto run
window.onload = changeLanguage;