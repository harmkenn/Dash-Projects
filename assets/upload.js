(function () {
    function setStatus(message, isError) {
        const status = document.getElementById("upload-status");
        if (!status) return;
        status.textContent = message;
        status.classList.toggle("status-error", Boolean(isError));
    }

    function uploadFile(file) {
        if (!file.name.toLowerCase().endsWith(".zip")) {
            setStatus("Choose a .zip archive.", true);
            return;
        }

        const form = new FormData();
        form.append("file", file, file.name);
        const request = new XMLHttpRequest();
        request.open("POST", "/upload-takeout");
        request.upload.addEventListener("progress", function (event) {
            if (event.lengthComputable) {
                const percent = Math.round((event.loaded / event.total) * 100);
                setStatus("Uploading ZIP... " + percent + "%", false);
            }
        });
        request.addEventListener("load", function () {
            let result;
            try {
                result = JSON.parse(request.responseText);
            } catch {
                if (request.status >= 400) {
                    const reason = request.status === 413 ? "The ZIP is too large for the server to accept." : "The server rejected the ZIP (HTTP " + request.status + ").";
                    setStatus(reason, true);
                    return;
                }
                setStatus("The upload response could not be read.", true);
                return;
            }
            if (request.status < 200 || request.status >= 300) {
                setStatus(result.error || "The ZIP could not be uploaded.", true);
                return;
            }
            setStatus("Uploaded " + result.filename + ". Scanning metadata...", false);
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props("uploaded-source", { data: result });
            } else {
                setStatus("Upload finished, but the app could not start scanning. Reload the page and try again.", true);
            }
        });
        request.addEventListener("error", function () {
            setStatus("Upload failed. Check that the app is still running and try again.", true);
        });
        request.send(form);
        setStatus("Preparing upload...", false);
    }

    function initializeDropzone() {
        const zone = document.getElementById("upload-dropzone");
        if (!zone || zone.dataset.ready) return;
        zone.dataset.ready = "true";

        const picker = document.createElement("input");
        picker.type = "file";
        picker.accept = ".zip,application/zip";
        picker.hidden = true;
        picker.addEventListener("change", function () {
            if (picker.files && picker.files[0]) uploadFile(picker.files[0]);
            picker.value = "";
        });
        zone.appendChild(picker);
        zone.addEventListener("click", function (event) {
            if (event.target !== picker) picker.click();
        });
        zone.addEventListener("keydown", function (event) {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                picker.click();
            }
        });
        zone.addEventListener("dragover", function (event) {
            event.preventDefault();
            zone.classList.add("is-dragging");
        });
        zone.addEventListener("dragleave", function () {
            zone.classList.remove("is-dragging");
        });
        zone.addEventListener("drop", function (event) {
            event.preventDefault();
            zone.classList.remove("is-dragging");
            if (event.dataTransfer.files && event.dataTransfer.files[0]) {
                uploadFile(event.dataTransfer.files[0]);
            }
        });
    }

    const observer = new MutationObserver(initializeDropzone);
    observer.observe(document.documentElement, { childList: true, subtree: true });
    document.addEventListener("DOMContentLoaded", initializeDropzone);
    initializeDropzone();
})();