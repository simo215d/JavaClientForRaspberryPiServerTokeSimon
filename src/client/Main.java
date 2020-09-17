package client;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.scene.Scene;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.Base64;
import java.util.Date;
import java.util.concurrent.TimeUnit;

public class Main extends Application {
    private static String fromServer;

    //hackerman stuff
    private static SecretKeySpec secretKey;
    private static byte[] key;

    //temperature graph fields
    private final NumberAxis tXAxis = new NumberAxis();
    private final NumberAxis tYAxis = new NumberAxis();
    private final LineChart<Number, Number> tGraph = new LineChart<>(tXAxis, tYAxis);
    private XYChart.Series tSeries = new XYChart.Series();
    //moist graph fields
    private final NumberAxis mXAxis = new NumberAxis();
    private final NumberAxis mYAxis = new NumberAxis();
    private final LineChart<Number, Number> mGraph = new LineChart<>(mXAxis, mYAxis);
    private XYChart.Series mSeries = new XYChart.Series();

    //vi bruger denne til at måle tidsforskel mellem start og en ny måling til vores x koordinater.
    private static Date startDate = new Date();

    @Override
    public void start(Stage primaryStage) throws Exception{
        //setting up graph for temperature
        tXAxis.setLabel("Time in seconds");
        tYAxis.setLabel("Temperature");
        tGraph.setTitle("Temperature over timer");
        tSeries.setName("Temperature data");
        tGraph.getData().add(tSeries);
        //graph Moist setup
        mXAxis.setLabel("Time in seconds");
        mYAxis.setLabel("Moisture");
        mGraph.setTitle("Moisture over timer");
        mSeries.setName("Moisture data");
        mGraph.getData().add(mSeries);
        //finalizing window

        primaryStage.setTitle("Java client - PI server");
        primaryStage.setScene(new Scene(new VBox(tGraph, mGraph), 500, 500));
        primaryStage.show();
        new Thread(new Runnable() {
            @Override
            public void run() {
                startClient();
            }
        }).start();
    }

    private void startClient(){
        try {
            //vi skal bruger ip og port fra vores PI så vi kan begynde socket forbindelsen
            Socket socket = new Socket("192.168.43.135", 8000);
            //vi bruger BufferedReader til at læse fra vores sockets inpurt stream som kommer fra serveren.
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            //hvert loop begynder med at vi venter på besked fra PI serveren. Når vi får en besked, så opdatere vi vores grafer.
            while (true){
                fromServer = in.readLine();
                System.out.println("received: " + fromServer);
                String decrypted = decrypt(fromServer);
                System.out.println("received decrypted: " + decrypted);
                //System.out.println("decrypted: " + decrypt(fromServer));
                //if server dies end program.
                if (fromServer == null) {
                    System.out.println("Server DEAD");
                    Platform.exit();
                    break;
                }
                //vi opdatere vores ui på Platform.runlater som laver en ny tråd, da loop ellers vil forhindre os i at opdatere ui samtidigt.
                Platform.runLater(new Runnable() {
                    @Override
                    public void run() {
                        System.out.println("t: "+decrypted.substring(1,3)+"m: "+decrypted.substring(4,6));
                        //her opdatere vi vores grafer med x=tid og y=måling
                        tSeries.getData().add(new XYChart.Data((int)getDateDiff(startDate, new Date(), TimeUnit.SECONDS), Integer.parseInt(decrypted.substring(1,3))));
                        mSeries.getData().add(new XYChart.Data((int)getDateDiff(startDate, new Date(), TimeUnit.SECONDS), Integer.parseInt(decrypted.substring(4,6))));
                    }
                });
            }
        } catch (Exception e){
            e.printStackTrace();
        }
    }

    //så vi ved hvor lang tid der er gået så vi kan placere vores x koordinat
    public static long getDateDiff(Date date1, Date date2, TimeUnit timeUnit) {
        long diffInMillies = date2.getTime() - date1.getTime();
        return timeUnit.convert(diffInMillies,TimeUnit.MILLISECONDS);
    }

    public static String decrypt(String strToDecrypt)
    {
        try
        {
            Cipher ci = Cipher.getInstance("AES/CBC/NoPadding");
            ci.init(Cipher.DECRYPT_MODE, new SecretKeySpec("Just a key123456".getBytes(), "AES"), new IvParameterSpec("Just an IV123456".getBytes()));
            byte[] b64dced = Base64.getDecoder().decode(strToDecrypt);
            //husk at beskeden skal være 16 lang.
            byte[] decd = ci.doFinal(b64dced);
            String message = new String(decd);
            System.out.println(message);
            return message;
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
        return null;
    }

    public static void main(String[] args) {
        launch(args);
    }
}
