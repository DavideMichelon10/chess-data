resource "google_sql_database" "new_database" {
  name     = "chess_data"
  instance = google_sql_database_instance.mysql.name
}

resource "google_sql_user" "mysql_user" {
  name     = "chess_admin"
  instance = google_sql_database_instance.mysql.name
  password = ""
  host     = "%"
}

resource "google_sql_database_instance" "mysql" {
  name             = "instance"
  database_version = "MYSQL_8_0_31"
  settings {
    tier    = "db-n1-standard-1"
    edition = "ENTERPRISE"
  }
}