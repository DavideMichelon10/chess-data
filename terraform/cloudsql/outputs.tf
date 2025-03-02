# output "db_instance_name" {
#   value = google_sql_database_instance.mysql.name
# }

# output "db_user" {
#   value = google_sql_user.mysql_user.name
# }

# output "db_password" {
#   value = google_sql_user.mysql_user.password
#   sensitive = true  # Nasconde il valore nei log Terraform
# }

# output "db_name" {
#   value = google_sql_database.new_database.name
# }

# output "db_host" {
#   value = google_sql_database_instance.mysql.public_ip_address
# }