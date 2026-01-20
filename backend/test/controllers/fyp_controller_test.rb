require "test_helper"

class FypControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get fyp_index_url
    assert_response :success
  end
end
