const isMobileScreen = window.innerWidth <= 1024;
let path = window.location.pathname;

// *Flash closing
function closeMessage()
{
    document.querySelector(".flash").style.display='none';
}

// *Navigation
document.querySelectorAll(".path").forEach(
    element => element.classList.remove("underline_nav_path")
)
if (path.endsWith("/"))
{
    document.querySelector(".home_path").classList.add("underline_nav_path");
}

else if (path.endsWith("/jobs"))
{
    document.querySelector(".jobs_path").classList.add("underline_nav_path");
}

else if (path.endsWith("/saved_jobs"))
{
    document.querySelector(".saved_jobs_path").classList.add("underline_nav_path");
}

else if (path.endsWith("/about"))
{
    document.querySelector(".about_path").classList.add("underline_nav_path");
}

// *Job search radio
function checkRadioLabel(label) 
{
    document.querySelectorAll(".radio_label").forEach(
        element => element.classList.remove("radio_label_checked")
    )
    label.classList.add("radio_label_checked")
}

// *AI robot 

// Open chat
async function aiRobotClicked()
{
    if (document.querySelector(".ai_chat").classList.contains("hidden")) 
    {
        document.querySelector(".ai_chat").classList.remove("hidden");
        document.querySelector(".chat_input_field").focus();

        const data = {
            requestedCategory: "firstMessage",
        }

        try
        {
            const response = await fetch("/js/ai_chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const responseData = await response.json();
            const newParagraph = document.createElement("p");
            newParagraph.textContent = responseData["message"];
            newParagraph.classList.add("inchat_ai_message")
            document.getElementById("ai_chat_window").appendChild(newParagraph);
        }
        catch (error) 
        {
            console.log("Error with communication between Flask and JavaScript.")
        }
    }
}

// Close chat
async function closeAiChat()
{
    // Delete messages in ai window
    document.querySelector("#ai_chat_window").replaceChildren();
    document.querySelector(".chat_input_field").value = '';
    
    // Delete ai chat history
    try 
    {
        const response = await fetch("/delete_ai_history", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

    }
    catch (error)
    {
        console.log("Error with communication between Flask and JavaScript.")
    }

    // Hide ai chat
    document.querySelector(".ai_chat").classList.add("hidden");

}

// If user presses enter while having an ai chat open
if (path.endsWith("/") || path.endsWith("/jobs") || path.endsWith("/saved") || path.endsWith("/about"))
{
    document.querySelector(".chat_input_field").addEventListener("keydown", (event) => {
    if (event.key === "Enter")
    {
        event.preventDefault();
        if (document.querySelector(".chat_input_field").value != "")
        {
            sentMessage();
        }

    }
    });
}

let aiResponded = true;

// Sent message
async function sentMessage()
{
    const chat_field = document.querySelector(".chat_input_field");
    
    const user_message = chat_field.value;
    if (user_message != "" && aiResponded == true)
    {
        aiResponded = false;
        chat_field.value = "";

        const user_message_p = document.createElement("p");
        user_message_p.textContent = user_message;
        user_message_p.classList.add("inchat_user_message");
        document.getElementById("ai_chat_window").appendChild(user_message_p);

        const data = {
            requestedCategory: "reply", 
            message: user_message
        };

        try 
        {
            const response = await fetch("/js/ai_chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            })

            const responseData = await response.json();
            
            // Adding response to the chat window
            const newParagraph = document.createElement("p");
            newParagraph.textContent = responseData;
            newParagraph.classList.add("inchat_ai_message");
            document.getElementById("ai_chat_window").appendChild(newParagraph);

            aiResponded = true;
        }
        catch (error)
        {
            console.log("Error with communication between Flask and JavaScript.")
        }
    }
    
}

// *Settings
function logOut()
{
    document.querySelector(".logging_out_message").classList.remove("hidden")
}

function closeLogOutWindow()
{
    document.querySelector(".logging_out_message").classList.add("hidden");
}

function addPhoto() 
{
    console.log("Pressed")
}