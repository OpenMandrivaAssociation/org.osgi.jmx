Name:		org.osgi.jmx
Version:	1.1.0
Release:	1
Summary:	OSGi JMX API
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.jmx/%{version}/org.osgi.jmx-%{version}-sources.jar

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.osgi:org.osgi.annotation.versioning)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
OSGi JMX 1.1. MBeans for the framework, wiring, Configuration Admin,
Permission Admin, Initial Provisioning, and User Admin. The MBeans use
javax.management from the JDK. Package versions are 1.1 for the root
and wiring packages, 1.7 for the framework package, 1.3 for
Configuration Admin, 1.2 for Permission Admin and Provisioning, and
1.1.1 for User Admin. Versioning annotations are compile-time only.
This build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
python - <<'PY'
from pathlib import Path

res = Path("src/main/resources")
for info in Path("org").rglob("packageinfo"):
    dest = res / info
    dest.parent.mkdir(parents=True, exist_ok=True)
    info.rename(dest)
Path("src/main/java").mkdir(parents=True)
Path("org").rename("src/main/java/org")

root = Path("src/main/java")
names = sorted(str(path.relative_to(root)) for path in root.rglob("*.java"))
expect = [
    "org/osgi/jmx/Item.java",
    "org/osgi/jmx/JmxConstants.java",
    "org/osgi/jmx/framework/BundleStateMBean.java",
    "org/osgi/jmx/framework/FrameworkMBean.java",
    "org/osgi/jmx/framework/PackageStateMBean.java",
    "org/osgi/jmx/framework/ServiceStateMBean.java",
    "org/osgi/jmx/framework/package-info.java",
    "org/osgi/jmx/framework/wiring/BundleWiringStateMBean.java",
    "org/osgi/jmx/framework/wiring/package-info.java",
    "org/osgi/jmx/package-info.java",
    "org/osgi/jmx/service/cm/ConfigurationAdminMBean.java",
    "org/osgi/jmx/service/cm/package-info.java",
    "org/osgi/jmx/service/permissionadmin/PermissionAdminMBean.java",
    "org/osgi/jmx/service/permissionadmin/package-info.java",
    "org/osgi/jmx/service/provisioning/ProvisioningServiceMBean.java",
    "org/osgi/jmx/service/provisioning/package-info.java",
    "org/osgi/jmx/service/useradmin/UserAdminMBean.java",
    "org/osgi/jmx/service/useradmin/package-info.java",
]
if names != expect:
    raise SystemExit("java files " + " ".join(names))
versions = {
    "org/osgi/jmx/package-info.java": '@Version("1.1")',
    "org/osgi/jmx/framework/package-info.java": '@Version("1.7")',
    "org/osgi/jmx/framework/wiring/package-info.java": '@Version("1.1")',
    "org/osgi/jmx/service/cm/package-info.java": '@Version("1.3")',
    "org/osgi/jmx/service/permissionadmin/package-info.java": '@Version("1.2")',
    "org/osgi/jmx/service/provisioning/package-info.java": '@Version("1.2")',
    "org/osgi/jmx/service/useradmin/package-info.java": '@Version("1.1.1")',
}
for rel, marker in versions.items():
    text = (root / rel).read_text(encoding="utf-8")
    if marker not in text:
        raise SystemExit("package-info version changed " + rel)
infos = {
    "org/osgi/jmx/packageinfo": b"version 1.1\n",
    "org/osgi/jmx/framework/packageinfo": b"version 1.7\n",
    "org/osgi/jmx/framework/wiring/packageinfo": b"version 1.1\n",
    "org/osgi/jmx/service/cm/packageinfo": b"version 1.3\n",
    "org/osgi/jmx/service/permissionadmin/packageinfo": b"version 1.2\n",
    "org/osgi/jmx/service/provisioning/packageinfo": b"version 1.2\n",
    "org/osgi/jmx/service/useradmin/packageinfo": b"version 1.1.1\n",
}
found = sorted(str(path.relative_to(res)) for path in res.rglob("packageinfo"))
if found != sorted(infos):
    raise SystemExit("packageinfo set " + " ".join(found))
for rel, blob in infos.items():
    got = (res / rel).read_bytes()
    if got != blob:
        raise SystemExit("packageinfo " + rel + " " + repr(got))
if list(root.rglob("packageinfo")):
    raise SystemExit("packageinfo still beside the sources")
if "Apache License" not in Path("LICENSE").read_text(encoding="utf-8"):
    raise SystemExit("LICENSE is not the Apache license")
if not Path("about.html").is_file():
    raise SystemExit("missing about.html")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.jmx</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:org.osgi.jmx</name>
  <description>OSGi JMX API.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.annotation.versioning</artifactId>
      <version>1.1.0</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>org.osgi.jmx</artifactId>",
    "<artifactId>org.osgi.annotation.versioning</artifactId>",
    "<version>1.1.0</version>",
    "<scope>provided</scope>",
    "<version>%{version}</version>",
    "<release>8</release>",
    "</project.build.sourceEncoding>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
if pom.count("<version>1.1.0</version>") != 2:
    raise SystemExit("version 1.1.0 count")
for needle in (
    "junit",
    "SNAPSHOT",
    "<source>",
    "<target>",
    "<parent>",
    "felix",
    "maven-bundle-plugin",
    "<artifactId>osgi.annotation</artifactId>",
    "<artifactId>osgi.core</artifactId>",
    "<version>1.1.1</version>",
    "<version>1.2</version>",
    "<version>1.3</version>",
    "<version>1.7</version>",
    "<version>8.0.1</version>",
    "<version>8.1.0</version>",
    "projectbuild.sourceEncoding",
):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.osgi.jmx-%{version}.jar --describe-module org.osgi.jmx > module-describe.txt
grep -q '^org.osgi.jmx' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }
python - <<'PY'
import zipfile
from pathlib import Path
jar = Path("target/org.osgi.jmx-%{version}.jar")
with zipfile.ZipFile(jar) as zf:
    names = set(zf.namelist())
    infos = {
        "org/osgi/jmx/packageinfo": b"version 1.1\n",
        "org/osgi/jmx/framework/packageinfo": b"version 1.7\n",
        "org/osgi/jmx/framework/wiring/packageinfo": b"version 1.1\n",
        "org/osgi/jmx/service/cm/packageinfo": b"version 1.3\n",
        "org/osgi/jmx/service/permissionadmin/packageinfo": b"version 1.2\n",
        "org/osgi/jmx/service/provisioning/packageinfo": b"version 1.2\n",
        "org/osgi/jmx/service/useradmin/packageinfo": b"version 1.1.1\n",
    }
    for rel, blob in infos.items():
        if zf.read(rel) != blob:
            raise SystemExit("jar packageinfo " + rel)
required = {
    "org/osgi/jmx/Item.class",
    "org/osgi/jmx/JmxConstants.class",
    "org/osgi/jmx/package-info.class",
    "org/osgi/jmx/framework/BundleStateMBean.class",
    "org/osgi/jmx/framework/FrameworkMBean.class",
    "org/osgi/jmx/framework/PackageStateMBean.class",
    "org/osgi/jmx/framework/ServiceStateMBean.class",
    "org/osgi/jmx/framework/package-info.class",
    "org/osgi/jmx/framework/wiring/BundleWiringStateMBean.class",
    "org/osgi/jmx/framework/wiring/package-info.class",
    "org/osgi/jmx/service/cm/ConfigurationAdminMBean.class",
    "org/osgi/jmx/service/cm/package-info.class",
    "org/osgi/jmx/service/permissionadmin/PermissionAdminMBean.class",
    "org/osgi/jmx/service/permissionadmin/package-info.class",
    "org/osgi/jmx/service/provisioning/ProvisioningServiceMBean.class",
    "org/osgi/jmx/service/provisioning/package-info.class",
    "org/osgi/jmx/service/useradmin/UserAdminMBean.class",
    "org/osgi/jmx/service/useradmin/package-info.class",
}
missing = sorted(required - names)
if missing:
    raise SystemExit("missing " + " ".join(missing))
extra = sorted(name for name in names if name.endswith(".class") and name not in required)
if extra:
    raise SystemExit("extra " + " ".join(extra))
if any("$" in name for name in names):
    raise SystemExit("unexpected inner class")
PY

%files -f .mfiles
%doc LICENSE about.html
