class FypController < ApplicationController
  def index
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
