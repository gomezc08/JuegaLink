class FypController < ApplicationController
  def index
  end

  def profile
    @user = current_user
    if @user && @user['username']
      friends_result = MlApiService.get_friends(username: @user['username'])
      @friends_count = friends_result['count'] || 0
    else
      @friends_count = 0
    end
  end

  def edit_profile
    @user = current_user
    unless @user
      redirect_to fyp_profile_path, alert: "You must be logged in to edit your profile"
    end
  end

  def update_profile
    unless current_user && current_user['username']
      redirect_to fyp_profile_path, alert: "You must be logged in to update your profile"
      return
    end

    result = MlApiService.update_user(
      username: current_user['username'],
      bio: params[:bio],
      email: params[:email],
      age: params[:age].present? ? params[:age].to_i : nil,
      city: params[:city],
      state: params[:state],
      phone_no: params[:phone_no]
    )

    if result['user']
      session[:user] = result['user']
      redirect_to fyp_profile_path, notice: "Profile updated successfully!"
    else
      redirect_to fyp_profile_path, alert: result[:error] || "Failed to update profile"
    end
  end

  def search
  end

  def login
    result = MlApiService.login(
      username: params[:username],
      password: params[:password]
    )

    if result['user']
      session[:user] = result['user']
      redirect_to fyp_index_path, notice: "Welcome back, #{result['user']['username']}!"
    else
      flash.now[:alert] = result[:error] || "Invalid username or password"
      redirect_to home_login_path, alert: result[:error] || "Invalid username or password"
    end
  end
end
