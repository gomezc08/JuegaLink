class FypController < ApplicationController
  def index
  end

  def profile
    @user = current_user
    if @user && @user['username']
      @followers_count = MlApiService.get_user_followers_count(username: @user['username']) || 0
      @following_count = MlApiService.get_user_following_count(username: @user['username']) || 0
    else
      @followers_count = 0
      @following_count = 0
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
        following_result = MlApiService.get_user_following(username: current_user['username'])
        if following_result && following_result['following'].is_a?(Array)
          @is_following = following_result['following'].include?(@user['username'])
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

  def unfollow
    unless current_user && current_user['username']
      redirect_to home_login_path, alert: "You must be logged in to unfollow users"
      return
    end

    result = MlApiService.unfollow_user(
      username: current_user['username'],
      unfollow_username: params[:unfollow_username]
    )

    if result['message']
      redirect_to fyp_user_page_path(username: params[:unfollow_username]), notice: "You have unfollowed #{params[:unfollow_username]}!"
    else
      redirect_to fyp_user_page_path(username: params[:unfollow_username]), alert: result[:error] || "Failed to unfollow user"
    end
  end

  def notifications
    unless current_user && current_user['username']
      redirect_to home_login_path, alert: "You must be logged in to view notifications"
      return
    end

    result = MlApiService.get_follow_requests(username: current_user['username'])
    if result && result['follow_requests'].is_a?(Array)
      # Transform array of usernames into array of hashes with 'username' key
      @follow_requests = result['follow_requests'].map { |username| { 'username' => username } }
    else
      @follow_requests = []
    end
  end
  
  def friends
    unless current_user && current_user['username']
      redirect_to home_login_path, alert: "You must be logged in to view friends"
      return
    end

    @is_followers = params[:is_followers] == 'true' || params[:is_followers] == '1'
    
    if @is_followers
      result = MlApiService.get_user_followers(username: current_user['username'])
      @friends_list = result && result['followers'].is_a?(Array) ? result['followers'] : []
      @page_title = "Followers"
    else
      result = MlApiService.get_user_following(username: current_user['username'])
      @friends_list = result && result['following'].is_a?(Array) ? result['following'] : []
      @page_title = "Following"
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
