class AddContactsToUsers < ActiveRecord::Migration[8.1]
  def change
    add_column :users, :email, :string
    add_column :users, :phone_no, :string
  end
end
