let menuicn = document.querySelector(".menuicn"); 
let nav = document.querySelector(".navcontainer"); 

menuicn.addEventListener("click", () => { 
	nav.classList.toggle("navclose"); 
})

const burgerBtn = document.querySelector('.burger');
const listItems = document.querySelector('.list-items');

burgerBtn.addEventListener('click', ()=>{
   listItems.classList.toggle('show');
})

