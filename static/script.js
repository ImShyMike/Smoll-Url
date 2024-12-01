const inputForm = document.getElementById("inputForm");
const urlInput = document.getElementById("urlInput");
const generatedUrlDisplay = document.getElementById("generatedUrl");
const generatedUrlContainer = document.getElementById("generatedUrlContainer");

inputForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = { url: urlInput.value };

    try {
        const response = await fetch("/create", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
            console.log("Response:", result);
            const generatedUrl = window.location.href + result.id;
            generatedUrlDisplay.value = generatedUrl;
            generatedUrlContainer.style.display = "block";

            document.getElementById("copyButton").onclick = function() {
                try {
                    navigator.clipboard.writeText(generatedUrl);
                    alert("Shortened URL copied to clipboard!");
                } catch (err) {
                    alert(`Failed to copy URL to clipboard (id: ${result.id})`);
                }
            }
        } else {
            alert("Error: " + result.error)
            console.error("Error:", result.error);
        }
    } catch (error) {
        alert("Fetch failed: " + error)
        console.error("Fetch failed:", error);
    }
});
