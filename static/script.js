const isMobileScreen = window.innerWidth <= 1024;
let path = window.location.pathname;

function closeMessage()
{
    document.querySelector(".flash").style.display='none';
}