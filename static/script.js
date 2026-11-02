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
    document.querySelector(".ai_chat").classList.remove("hidden");

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
        console.log(responseData);
    }
    catch (error) 
    {
        console.log("Error with communication between Flask and JavaScript.")
    }
}

// Close chat
function closeAiChat()
{
    document.querySelector(".ai_chat").classList.add("hidden");
}

// 
async function sentMessage()
{
    const user_message = document.querySelector(".chat_input_field").value;

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
        
        console.log(responseData)
    }
    catch (error)
    {
        console.log("Error with communication between Flask and JavaScript.")
    }
}