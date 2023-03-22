let scanBtn = document.getElementById("scan_btn"),
    stopBtn = document.getElementById("stop_btn"),
    bar_code = document.querySelector("#barcode"),
    validityCheck = document.querySelector(".validity_check"),
    barcodeRes = document.querySelector("#barcode_res"),
    newStudentReg = document.querySelector(".new_student_reg");;

bar_code.style.display = "none";

const quaggaInit = () => {
    Quagga.init(
        {
            inputStream: {
                type: "LiveStream",
                constraints: {
                    width: 640,
                    height: 360,
                    facingMode: "environment",
                },
            },
            locator: {
                patchSize: "medium",
                halfSample: true,
            },
            numOfWorkers: navigator.hardwareConcurrency
                ? navigator.hardwareConcurrency
                : 4,
            decoder: {
                readers: [
                    "code_128_reader",
                    "ean_reader",
                    "ean_8_reader",
                    "code_39_reader",
                    "code_39_vin_reader",
                    "codabar_reader",
                    "upc_reader",
                    "upc_e_reader",
                    "i2of5_reader",
                ],
                debug: {
                    showCanvas: true,
                    showPatches: true,
                    showFoundPatches: true,
                    showSkeleton: true,
                    showLabels: true,
                    showPatchLabels: true,
                    showRemainingPatchLabels: true,
                    boxFromPatches: {
                        showTransformed: true,
                        showTransformedBox: true,
                        showBB: true,
                    },
                },
            },
        },
        function (err) {
            if (err) {
                document.getElementById("v").innerHTML = err;
                return;
            }
            document.getElementById("v").innerHTML =
                "Initialization finished. Ready to start";
            Quagga.start();
        }
    );
};

const alert_trigger = (type, msg) =>{
    return `
        <div class="alert alert-${type}" role="alert">
            <p class="mb-0">${msg}</p>
        </div>`;
}

scanBtn.addEventListener("click", () => {
    let status = scanBtn.getAttribute("data-status");
    notification.innerHTML = alert_trigger("none",``);
    if(newStudentReg) newStudentReg.classList.remove("show");
    validityCheck.classList.remove("show");
    if (status === "false") {
        document.getElementById("interactive").style.display = "block";
        quaggaInit();
        scanBtn.setAttribute("data-status", "true");
    }
});

stopBtn.addEventListener("click", () => {
    let status = scanBtn.getAttribute("data-status");
    if (status === "true") {
        Quagga.stop();
        scanBtn.setAttribute("data-status", "false");
        document.getElementById("interactive").style.display = "none";
    }
});

Quagga.onDetected(function (result) {
    document.getElementById("v").innerHTML = result.codeResult.code;
    bar_code.style.display = "block";
    JsBarcode("#barcode", `${result.codeResult.code}`);
    document.getElementById("barcode").querySelector("rect").style.fill = "#ffffff00"
    validityCheck.classList.add("show");
    validityCheck.setAttribute("code",result.codeResult.code);
    barcodeRes.innerHTML = result.codeResult.code
});