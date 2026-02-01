require 'net/http'
require 'json'
require 'uri'

class MlApiService
  BASE_URL = ENV.fetch('ML_SERVICE_URL', 'http://localhost:5000')

  class << self
    def signup(username:, email:, password:)
      uri = URI("#{BASE_URL}/users/signup")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        username: username,
        email: email,
        password: password
      }.to_json

      response = http.request(request)
      handle_response(response)
    end

    def login(username:, password:)
      uri = URI("#{BASE_URL}/users/login")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        username: username,
        password: password
      }.to_json

      response = http.request(request)
      handle_response(response)
    end

    def update_user(username:, **params)
      uri = URI("#{BASE_URL}/users/update")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Put.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        username: username,
        **params
      }.to_json

      response = http.request(request)
      handle_response(response)
    end

    def get_friends(username:)
      uri = URI("#{BASE_URL}/users/#{username}/friends")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Get.new(uri.path, 'Content-Type' => 'application/json')

      response = http.request(request)
      handle_response(response)
    end

    def get_user(username:)
      uri = URI("#{BASE_URL}/users/#{username}")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Get.new(uri.path, 'Content-Type' => 'application/json')
      response = http.request(request)
      handle_response(response)
    end

    def get_event(event_name:)
      uri = URI("#{BASE_URL}/events/get")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        event_name: event_name
      }.to_json
      response = http.request(request)
      handle_response(response)
    end

    def search_users(query:)
      uri = URI("#{BASE_URL}/search/users")
      uri.query = URI.encode_www_form(q: query)
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Get.new(uri.path + '?' + uri.query, 'Content-Type' => 'application/json')

      response = http.request(request)
      handle_response(response)
    end

    def search_events(query:)
      uri = URI("#{BASE_URL}/search/events")
      uri.query = URI.encode_www_form(q: query)
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Get.new(uri.path + '?' + uri.query, 'Content-Type' => 'application/json')

      response = http.request(request)
      handle_response(response)
    end

    def follow_user(username:, follow_username:)
      uri = URI("#{BASE_URL}/users/follow")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        username: username,
        follow_username: follow_username
      }.to_json

      response = http.request(request)
      handle_response(response)
    end

    def unfollow_user(username:, unfollow_username:)
      uri = URI("#{BASE_URL}/users/unfollow")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        username: username,
        unfollow_username: unfollow_username
      }.to_json

      response = http.request(request)
      handle_response(response)
    end

    def get_user_followers(username:)
      uri = URI("#{BASE_URL}/users/followers")
      uri.query = URI.encode_www_form(username: username)
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Get.new(uri.path + '?' + uri.query, 'Content-Type' => 'application/json')
      response = http.request(request)
      handle_response(response)
    end

    def get_user_followers_count(username:)
      result = get_user_followers(username: username)
      if result && result['followers'].is_a?(Array)
        result['followers'].length
      else
        0
      end
    end

    def get_user_following(username:)
      uri = URI("#{BASE_URL}/users/following")
      uri.query = URI.encode_www_form(username: username)
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Get.new(uri.path + '?' + uri.query, 'Content-Type' => 'application/json')
      response = http.request(request)
      handle_response(response)
    end

    def get_user_following_count(username:)
      result = get_user_following(username: username)
      if result && result['following'].is_a?(Array)
        result['following'].length
      else
        0
      end
    end

    def get_follow_requests(username:)
      uri = URI("#{BASE_URL}/users/follow_requests")
      uri.query = URI.encode_www_form(username: username)
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Get.new(uri.path + '?' + uri.query, 'Content-Type' => 'application/json')
      response = http.request(request)
      handle_response(response)
    end

    def accept_follow_request(username:, accept_username:)
      uri = URI("#{BASE_URL}/users/accept_follow_request")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        username: username,
        accept_username: accept_username
      }.to_json
      response = http.request(request)
      handle_response(response)
    end

    def reject_follow_request(username:, reject_username:)
      uri = URI("#{BASE_URL}/users/reject_follow_request")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        username: username,
        reject_username: reject_username
      }.to_json
      response = http.request(request)
      handle_response(response)
    end

    def get_post(id:)
      uri = URI("#{BASE_URL}/posts/get-by-id")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { post_id: id }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def get_post_comments(id:)
      uri = URI("#{BASE_URL}/posts/get-comments")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { post_id: id }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def create_post(title:, content:, event_name_mention:, username:)
      uri = URI("#{BASE_URL}/posts/create")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { title: title, content: content, event_name_mention: event_name_mention, username: username }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def delete_post(id:)
      uri = URI("#{BASE_URL}/posts/delete")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { post_id: id }.to_json
      request = Net::HTTP::Delete.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def like_post(username:, id:)
      uri = URI("#{BASE_URL}/posts/like")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { username: username, post_id: id }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def unlike_post(username:, id:)
      uri = URI("#{BASE_URL}/posts/unlike")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { username: username, post_id: id }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def comment_post(username:, id:, comment:)
      uri = URI("#{BASE_URL}/posts/comment")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { username: username, post_id: id, comment: comment }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def get_user_posts(username:)
      uri = URI("#{BASE_URL}/posts/get")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { username: username }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def get_events_joined_by_user(username:)
      uri = URI("#{BASE_URL}/events/list-joined-by-user")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { username: username }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def get_events_hosted_by_user(username:)
      uri = URI("#{BASE_URL}/events/list-hosted-by-user")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { username: username }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def list_attendees(event_name:)
      uri = URI("#{BASE_URL}/events/list-attendees")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { event_name: event_name }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def list_attendees_excluding_user(event_name:, username:)
      uri = URI("#{BASE_URL}/events/list-attendees")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { event_name: event_name, exclude_username: username }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def create_event(event_name:, username:, description:, date_time:, max_players:)
      uri = URI("#{BASE_URL}/events/create")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        event_name: event_name,
        username: username,
        description: description,
        date_time: date_time,
        max_players: max_players,
      }.to_json
      response = http.request(request)
      handle_response(response)
    end

    def delete_event(event_name:)
      uri = URI("#{BASE_URL}/events/delete")
      http = Net::HTTP.new(uri.host, uri.port)
      request = Net::HTTP::Delete.new(uri.path, 'Content-Type' => 'application/json')
      request.body = {
        event_name: event_name,
      }.to_json
      response = http.request(request)
      handle_response(response)
    end 

    def join_event(username:, event_name:)
      uri = URI("#{BASE_URL}/events/joined-by-user")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { username: username, event_name: event_name }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    def unjoin_event(username:, event_name:)
      uri = URI("#{BASE_URL}/events/left-by-user")
      http = Net::HTTP.new(uri.host, uri.port)
      body = { username: username, event_name: event_name }.to_json
      request = Net::HTTP::Post.new(uri.request_uri)
      request['Content-Type'] = 'application/json'
      request['Content-Length'] = body.bytesize.to_s
      request.body = body
      response = http.request(request)
      handle_response(response)
    end

    private

    def handle_response(response)
      case response.code.to_i
      when 200..299
        JSON.parse(response.body)
      when 401
        error_data = JSON.parse(response.body) rescue { error: 'Invalid credentials' }
        { error: error_data['error'] || 'Invalid credentials', success: false }
      when 400..499
        error_data = JSON.parse(response.body) rescue { error: 'Client error' }
        { error: error_data['error'] || 'Client error', success: false }
      when 500..599
        error_data = JSON.parse(response.body) rescue { error: 'Server error' }
        { error: error_data['error'] || 'Server error', success: false }
      else
        { error: "Unexpected response: #{response.code}", success: false }
      end
    end
  end
end
