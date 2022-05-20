<?php
class SubsController extends Controller
{
    public function __construct()
    {
        parent::__construct();
    }

    public function store($router)
    {
        $email = $_POST['email'];

        if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
            header('Location: /?success=false&msg=Please submit a valild email address!');
            exit;
        }

        $subscriber = new SubscriberModel;
        $subscriber->subscribe($email);

        header('Location: /?success=true&msg=Email subscribed successfully!');
        exit;
    }

    public function logout($router)
    {
        session_destroy();
        header('Location: /admin');
        exit;
    }
}