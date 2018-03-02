#include<stdio.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<netinet/in.h>
#include<arpa/inet.h>
#include<string.h>
#include<stdlib.h>
#include<unistd.h>
#include<fcntl.h>
static void Use(const char* proc)
{
    printf("%s [server_ip] [server_port]\n",proc);
}
int main(int argc,char* argv[])
{
    if(argc!=3)
    {
        Use(argv[0]);
        return 1;
    }
    int sock = socket(AF_INET,SOCK_STREAM,0);
    if(sock<0)
    {
        perror("socket");
        return 2;
    }
    //close(1);
    //dup(sock);
    dup2(sock,1);
    struct sockaddr_in peer;
    peer.sin_family = AF_INET;
    peer.sin_port = htons(atoi(argv[2]));
    peer.sin_addr.s_addr = inet_addr(argv[1]);
    if(connect(sock,(struct sockaddr*)&peer,sizeof(peer))<0)
    {
        perror("connect");
        return 3;
    }
    char buf[1024];
    while(1)
    {
        memset(buf,0x00,1024);
        printf("please enter#");

        fflush(stdout);
        sleep(5);
//        close(1);
        dup2(sock,1);
        printf("x\n");
        fflush(stdout);

        ssize_t s = read(0,buf,sizeof(buf)-1);
        printf("t\n");
        fflush(stdout);
        if(s>0)
        {
            buf[s-1]=0;
            //write(sock,buf,strlen(buf));
            printf("write:%s\n",buf);
            ssize_t _s = read(sock,buf,sizeof(buf)-1);
            if(_s>0)
            {
                buf[_s]=0;
                printf("server echo#(%s)\n",buf);
            }
        }
        else{
            printf("ECHO \n");
            fflush(stdout);
        } 
    }
    close(sock);
    return 0;
}
