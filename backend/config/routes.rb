Rails.application.routes.draw do
  devise_for :users
  post "fyp/login", to: "fyp#login"
  get "fyp/index"
  get "fyp/profile"
  get "fyp/edit_profile"
  get "fyp/create_post", to: "fyp#create_post", as: :fyp_create_post
  post "fyp/create_post", to: "fyp#create_post_post", as: :fyp_create_post_post
  get "fyp/post/:id", to: "fyp#post", as: :fyp_post
  patch "fyp/profile", to: "fyp#update_profile"
  put "fyp/profile", to: "fyp#update_profile"
  get "fyp/search"
  root "home#index"
  get "fyp/user_page/:username", to: "fyp#user_page", as: :fyp_user_page
  get "fyp/event_page/:event_name", to: "fyp#event_page", as: :fyp_event_page
  post "fyp/join_event", to: "fyp#join_event", as: :fyp_join_event
  post "fyp/unjoin_event", to: "fyp#unjoin_event", as: :fyp_unjoin_event
  post "fyp/follow", to: "fyp#follow", as: :fyp_follow
  post "fyp/unfollow", to: "fyp#unfollow", as: :fyp_unfollow
  post "fyp/accept_follow_request", to: "fyp#accept_follow_request", as: :fyp_accept_follow_request
  post "fyp/reject_follow_request", to: "fyp#reject_follow_request", as: :fyp_reject_follow_request
  get "fyp/friends", to: "fyp#friends", as: :fyp_friends
  get "fyp/notifications", to: "fyp#notifications", as: :fyp_notifications
  get "fyp/create_event", to: "fyp#create_event", as: :fyp_create_event
  post "fyp/create_event", to: "fyp#create_event_post", as: :fyp_create_event_post
  delete "fyp/delete_event", to: "fyp#delete_event", as: :fyp_delete_event
  get "home/login"
  post "home/login", to: "home#login_post"
  get "home/signup"
  post "home/signup", to: "home#signup_post"
  delete "home/logout", to: "home#logout", as: :home_logout

  # Health check
  get "up" => "rails/health#show", as: :rails_health_check
end