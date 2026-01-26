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
    @query = params[:q] || ''
    @filter = params[:filter] || 'user'
    @results = []
    
    if @query.present?
      if @filter == 'user'
        result = MlApiService.search_users(query: @query)
        @results = result['users'] || []
        @count = result['count'] || 0
      elsif @filter == 'field'
        result = MlApiService.search_fields(query: @query)
        @results = result['fields'] || []
        @count = result['count'] || 0
      end
    else
      @count = 0
    end
  end

  def user_page
    @username = params[:username]
    result = MlApiService.get_user(username: @username)
    if result['user']
      @user = result['user']
      
      # Check if current user is following this user
      @is_following = false
      if current_user && current_user['username'] && current_user['username'] != @user['username']
        followers_result = MlApiService.get_user_followers(username: current_user['username'])
        if followers_result && followers_result['followers'].is_a?(Array)
          @is_following = followers_result['followers'].include?(@user['username'])
        end
      end
    else
      redirect_to fyp_search_path, alert: result[:error] || "User not found"
    end
  end

  def follow
    unless current_user && current_user['username']
      redirect_to home_login_path, alert: "You must be logged in to follow users"
      return
    end

    follow_username = params[:follow_username]
    unless follow_username.present?
      redirect_to fyp_search_path, alert: "Invalid user to follow"
      return
    end

    result = MlApiService.follow_user(
      username: current_user['username'],
      follow_username: follow_username
    )

    if result['message']
      redirect_to fyp_user_page_path(username: follow_username), notice: "You are now following #{follow_username}!"
    else
      redirect_to fyp_user_page_path(username: follow_username), alert: result[:error] || "Failed to follow user"
    end
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
