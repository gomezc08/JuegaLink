Rails.application.routes.draw do
  # root.
  root "home#index"

  # devise.
  devise_for :users

  # home.
  # authentication.
  get "home/login"
  get "home/signup"
  post "home/login", to: "home#login_post"
  post "fyp/login", to: "fyp#login"
  post "home/signup", to: "home#signup_post"
  delete "home/logout", to: "home#logout", as: :home_logout

  # fyp.
  # homepage.
  get "fyp/index"

  # header.
  get "fyp/search"
  get "fyp/notifications", to: "fyp#notifications", as: :fyp_notifications
  get "fyp/create_post", to: "fyp#create_post", as: :fyp_create_post
  get "fyp/profile"

  # profile.
  get "fyp/edit_profile"
  patch "fyp/profile", to: "fyp#update_profile"
  put "fyp/profile", to: "fyp#update_profile"

  # post.
  get "fyp/post/:id", to: "fyp#post", as: :fyp_post
  get "fyp/friends_posts", to: "fyp#friends_posts", as: :fyp_friends_posts
  post "fyp/create_post", to: "fyp#create_post_post", as: :fyp_create_post_post
  delete "fyp/delete_post", to: "fyp#delete_post", as: :fyp_delete_post

  # post engagement.
  post "fyp/like_post", to: "fyp#like_post", as: :fyp_like_post
  post "fyp/unlike_post", to: "fyp#unlike_post", as: :fyp_unlike_post
  post "fyp/comment_post", to: "fyp#comment_post", as: :fyp_comment_post

  # event.
  get "fyp/event_page/:event_name", to: "fyp#event_page", as: :fyp_event_page
  get "fyp/create_event", to: "fyp#create_event", as: :fyp_create_event
  get "fyp/list_attendees/:event_name", to: "fyp#list_attendees", as: :fyp_list_attendees
  get "fyp/list_attendees_excluding_user/:event_name/:username", to: "fyp#list_attendees_excluding_user", as: :fyp_list_attendees_excluding_user
  post "fyp/create_event", to: "fyp#create_event_post", as: :fyp_create_event_post
  post "fyp/join_event", to: "fyp#join_event", as: :fyp_join_event
  post "fyp/unjoin_event", to: "fyp#unjoin_event", as: :fyp_unjoin_event
  delete "fyp/delete_event", to: "fyp#delete_event", as: :fyp_delete_event

  # other users.
  get "fyp/user_page/:username", to: "fyp#user_page", as: :fyp_user_page
  get "fyp/friends", to: "fyp#friends", as: :fyp_friends
  
  # follow requests
  post "fyp/follow", to: "fyp#follow", as: :fyp_follow
  post "fyp/unfollow", to: "fyp#unfollow", as: :fyp_unfollow
  post "fyp/accept_follow_request", to: "fyp#accept_follow_request", as: :fyp_accept_follow_request
  post "fyp/reject_follow_request", to: "fyp#reject_follow_request", as: :fyp_reject_follow_request
  
  # Health check
  get "up" => "rails/health#show", as: :rails_health_check
end