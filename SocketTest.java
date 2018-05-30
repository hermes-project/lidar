import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.Inet4Address;
import java.net.ServerSocket;
import java.net.Socket;

public class Main {
    public static void main(String[] args) throws IOException {
        ServerSocket server;
        Socket lidar;
        server = new ServerSocket(15550);

        System.out.println("STARTING PYTHON");
        ProcessBuilder pb = new ProcessBuilder("python3","/home/tic-tac/projects/lidar/main.py");
        pb.directory(new File("/home/tic-tac/projects/lidar/"));
        pb.inheritIO();
        Process pr = pb.start();
        System.out.println("Waiting for lidar");
        lidar=server.accept();
        System.out.println("Lidar Connected");
        long moy=0;
        long n=0;
        Runtime.getRuntime().addShutdownHook(
                new Thread(()->{
                    try {
                        System.out.println("STOPPING BECAUSE OF SIGINT");
                        lidar.close();
                        server.close();
                        Runtime.getRuntime().exec("kill -f -SIGINT "+Integer.toString((int)pr.pid()));
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                })
        );

        BufferedReader input = new BufferedReader(new InputStreamReader(lidar.getInputStream()));
        String message="";
        long last = System.currentTimeMillis();

        while(true){
            if(input.ready()){
                message=input.readLine();
                n++;
                long now = System.currentTimeMillis();
                moy+=now-last;
                System.out.println(now-last+" "+message);
                System.out.println("Temps moyen d'echantillonnage:"+moy/n);
                last=now;
            }
        }
    }
}
