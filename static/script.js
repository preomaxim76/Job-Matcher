const isMobileScreen = window.innerWidth <= 1024;
let path = window.location.pathname;

// Flash closing
function closeMessage()
{
    document.querySelector(".flash").style.display='none';
}

// Navigation
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

function checkRadioLabel(label) 
{
    document.querySelectorAll(".radio_label").forEach(
        element => element.classList.remove("radio_label_checked")
    )
    label.classList.add("radio_label_checked")
}