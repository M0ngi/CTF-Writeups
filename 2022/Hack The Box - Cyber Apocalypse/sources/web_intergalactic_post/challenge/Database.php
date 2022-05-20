<?php
class Database
{
    private static $database = null;

    public function __construct($file)
    {
        if (!file_exists($file))
        {
            file_put_contents($file, '');
        }
        $this->db = new SQLite3($file);
        $this->migrate();

        self::$database = $this;
    }

    public static function getDatabase(): Database
    {
        return self::$database;
    }

    public function migrate()
    {
        $this->db->query('
            CREATE TABLE IF NOT EXISTS `subscribers` (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL
            );
        ');
    }

    public function subscribeUser($ip_address, $email)
    {
        return $this->db->exec("INSERT INTO subscribers (ip_address, email) VALUES('$ip_address', '$email')");
    }
}