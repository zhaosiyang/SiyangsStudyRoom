var oldWindowWidth = window.innerWidth;
var registerBoxWidth = $(".RegisterBox").css("width");

if(oldWindowWidth >= 992){
	$(".RegisterBox").css("height", registerBoxWidth);
	$("#signUpBox").css("height", "50%");
	$("#logInBox").css("height", "50%");
}

$(window).resize(function(){
	var newWindowWidth = window.innerWidth;
	var registerBoxWidth = $(".RegisterBox").css("width");
	if(oldWindowWidth < 992 && newWindowWidth >= 992){
		$(".RegisterBox").css("height", registerBoxWidth);
	}
	if(oldWindowWidth >= 992 && newWindowWidth <992){
		$(".RegisterBox").css("height", "100px");
	}
	if(newWindowWidth >= 992){
		$(".RegisterBox").css("height", registerBoxWidth);
	}
	oldWindowWidth = newWindowWidth;
});

$("#signUpSubmit").click(function(){
	var username = $("#inputUsername").val();
	var password1 = $("#inputPassword1").val();
	var password2 = $("#inputPassword2").val();
	var email = $("#inputEmail").val();
	var phone = $("#inputPhoneNumber").val();
	var firstName = $("#inputFirstName").val();
	var lastName = $("#inputLastName").val();
	var error = 0;
	$("#signUpError").html("");  //clear error area
	if(username.length < 4){
		$("#signUpError").append('<div class="alert alert-danger" role="alert">Username should be at least 4 characters or digits</div>');
		error = 1;
	}
	if(password1.length < 7){
		$("#signUpError").append('<div class="alert alert-danger" role="alert">Password should be at least 7 characters or digits</div>');
		error = 2;
	}
	if(password1 != password2){
		$("#signUpError").append('<div class="alert alert-danger" role="alert">The two passwords do not match</div>');
		error = 3;
	}
	if(firstName == ""){
		$("#signUpError").append('<div class="alert alert-danger" role="alert">Please enter your first name</div>');
		error = 4;
	}
	if(lastName == ""){
		$("#signUpError").append('<div class="alert alert-danger" role="alert">Please enter your last name</div>');
		error = 5;
	}
	if(phone == ""){
		$("#signUpError").append('<div class="alert alert-danger" role="alert">Please enter your phone number</div>');
		error = 6;
	}
	if(email == ""){
		$("#signUpError").append('<div class="alert alert-danger" role="alert">Please enter your email address</div>');
		error = 7;
	}
	if(error == 0){
		$.post("/signUp",{
			username: username,
			password: password1,
			firstName: firstName,
			lastName: lastName,
			phone: phone,
			email: email
		},function(data){
			if(data == "1"){
				$("#signUpError").append('<div class="alert alert-danger" role="alert">Username Already Exist</div>');
			}
			else{
				alert("Account Created Successfully!");
				$("#signUpCloseButton").trigger("click");
				document.cookie=data;
				window.location.replace("/manage?username="+username);
			}
		});
	}
});

$("#logInSubmit").click(function(){
	var username = $("#inputUsernameInLogIn").val()
	var password = $("#inputPasswordInLogIn").val()
	$("#logInError").html("");
	if (username == ""){
		$("#logInError").append('<div class="alert alert-danger" role="alert">Please enter your username</div>');
	}
	else if (password == ""){
		$("#logInError").append('<div class="alert alert-danger" role="alert">Please enter your password</div>');
	}
	else{
		$.post("/logIn", {username:username, password:password}, function(data){
			if(data == "The username does not exist!"){
				$("#logInError").append('<div class="alert alert-danger" role="alert">The username does not exist!</div>');
			}
			else if(data == "Incorrect password!"){
				$("#logInError").append('<div class="alert alert-danger" role="alert">Incorrect password!</div>');
			}
			else{   //successful
				document.cookie=data;
				window.location.replace("/manage?username="+username);
			}
		})
	}
	
});
"The username does not exist!"

$("#logOut").click(function(){
	document.cookie = "username=null";
});
$(".reserveButtonNotLoggedIn").click(function(){
	alert("Please sign up or log in before reserve a seat!");
});
$(".reserveButtonOK").click(function(){
	classID = $(this).attr("id");
	$.post("/manage",{classID: classID},function(data){
		if(data == "yes"){     //enough money
			if (confirm('Money will be deducted and you can NOT cancel the reservation. Are you sure to continue?')) {
			    $.post("/makeReservation", {classID:classID}, function(data){
			    	alert(data);
			    	location.reload()
			    });
			} 
		}
		else if (data == "lackMoney"){                  //not enough money
			alert("Your money is not enough");
		}
		else if (data == "sessionExpired"){
			alert("Your log session has expired, please log in again!");
			window.location.replace("/");
		}
		else if (data == "alreadyReserved"){
			alert("You have already reserved this class, no need to do it again!");
		}
		else if (data == "full"){
			alert("Sorry, the class is full");
		}
	})
	
});





