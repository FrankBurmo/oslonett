#define MAILTO  "mailto"
#define SUBJECT "subject"

#define ONMARKET "marketplace@oslonett.no"
#define OSLONETT "oslonett@oslonett.no"

typedef struct {
    char name[256];
    char val[2048];
} entry;


typedef struct {
	char           *name;
	char           *val;
}               pentry;

void            getword (char *word, char *line, char stop);

char            x2c (char *what);
void            unescape_url (char *url);
void            plustospace (char *str);
char           *daytime ();
char           *getenv();
