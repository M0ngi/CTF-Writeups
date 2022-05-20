<?php
class SubscriberModel extends Model
{

    public function __construct()
    {
        parent::__construct();
    }

    public function getSubscriberIP(){
        if (array_key_exists('HTTP_X_FORWARDED_FOR', $_SERVER)){
            return  $_SERVER["HTTP_X_FORWARDED_FOR"];
        }else if (array_key_exists('REMOTE_ADDR', $_SERVER)) {
            return $_SERVER["REMOTE_ADDR"];
        }else if (array_key_exists('HTTP_CLIENT_IP', $_SERVER)) {
            return $_SERVER["HTTP_CLIENT_IP"];
        }
        return '';
    }

    public function subscribe($email)
    {
        $ip_address = $this->getSubscriberIP();
        error_log("SUBSCRIBE: " . $ip_address . "\n");
        return $this->database->subscribeUser($ip_address, $email);
    }
}
