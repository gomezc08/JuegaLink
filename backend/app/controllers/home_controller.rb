class HomeController < ApplicationController
  def index
  end

  def login
  end

  def login_post
    result = MlApiService.login(
      username: params[:username],
      password: params[:password]
    )

    if result['user']
      session[:user] = result['user']
      redirect_to root_path, notice: "Welcome back, #{result['user']['username']}!"
    else
      flash.now[:alert] = result[:error] || "Invalid username or password"
      render :login, status: :unprocessable_entity
    end
  end

  def signup
  end

  def signup_post
    # Validate password confirmation
    if params[:password] != params[:password_confirmation]
      flash.now[:alert] = "Passwords do not match"
      render :signup, status: :unprocessable_entity
      return
    end

    # Call Flask API
    result = MlApiService.signup(
      username: params[:username],
      email: params[:email],
      password: params[:password]
    )

    if result['user']
      session[:user] = result['user']
      redirect_to home_login_path, notice: "Account created successfully! Welcome, #{result['user']['username']}!"
    else
      flash.now[:alert] = result[:error] || "Failed to create account"
      render :signup, status: :unprocessable_entity
    end
  end

  def logout
    session[:user] = nil
    redirect_to root_path, notice: "You have been logged out successfully."
  end
end
